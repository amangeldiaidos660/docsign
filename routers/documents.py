from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from db.session import SessionLocal
from db.models import User, Document, DocumentParticipant
from pydantic import BaseModel, Field
from typing import List
from services.registration_service import register_document


router = APIRouter(prefix="/documents", tags=["documents"])

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get("/partners")
async def search_partners(
    q: str = Query(..., min_length=2, alias="query"),
    limit: int = Query(10, ge=1, le=50),
    uid: int | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
):
    qv = q.strip()
    sim_full = func.similarity(User.full_name, qv)
    sim_org = func.similarity(User.organization, qv)
    sim_email = func.similarity(User.email, qv)
    sim_iin = func.similarity(User.iin, qv)
    sim_bin = func.similarity(User.bin, qv)

    stmt = (
        select(User.id, User.iin, User.bin, User.full_name, User.organization, User.email)
        .where(
            or_(
                sim_full > 0.2,
                sim_org > 0.2,
                sim_email > 0.2,
                sim_iin > 0.2,
                sim_bin > 0.2,
            )
        )
        .order_by(func.greatest(sim_full, sim_org, sim_email, sim_iin, sim_bin).desc())
        .limit(limit)
    )
    res = await session.execute(stmt)
    rows = res.all()
    items = []
    for row in rows:
        item = {
            "id": row.id,
            "iin": row.iin,
            "bin": row.bin,
            "full_name": row.full_name,
            "organization": row.organization,
            "email": row.email,
        }
        if uid is not None and row.id == uid:
            continue
        items.append(item)
    return {"results": items}


class CreateDocumentPayload(BaseModel):
    title: str | None = None
    file_name: str = Field(..., min_length=1)
    file_base64: str = Field(..., min_length=10)
    signature: str | None = None
    participant_user_ids: List[int] = Field(default_factory=list)


@router.post("")
async def create_document(
    payload: CreateDocumentPayload,
    uid: int | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
):
    if uid is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    
    
    unique_partners = list(dict.fromkeys([pid for pid in payload.participant_user_ids if pid != uid]))
    if len(unique_partners) > 4:
        raise HTTPException(status_code=400, detail="max 4 partners allowed")

   
    res = await session.execute(select(User.id).where(User.id.in_(unique_partners + [uid])))
    found_ids = {row.id for row in res}
    missing = set(unique_partners + [uid]) - found_ids
    if missing:
        raise HTTPException(status_code=400, detail=f"unknown user ids: {sorted(list(missing))}")

    if not payload.signature:
        raise HTTPException(status_code=400, detail="signature is required for document registration")


    doc = Document(
        owner_id=uid,
        title=payload.title,
        file_name=payload.file_name,
        file_base64=payload.file_base64,
        file_path="",
        status="pending",
    )
    session.add(doc)
    await session.flush()
    
    
    initiator_part = DocumentParticipant(
        document_id=doc.id,
        user_id=uid,
        role="initiator",
        status="pending",
    )
    session.add(initiator_part)
    

    
    for pid in unique_partners:
        participant = DocumentParticipant(
            document_id=doc.id,
            user_id=pid,
            role="signer",
            status="pending",
        )
        session.add(participant)
        

    await session.flush()
    
   
    check_stmt = select(DocumentParticipant).where(DocumentParticipant.document_id == doc.id)
    check_result = await session.execute(check_stmt)
    participants = check_result.scalars().all()
    
    
    registration_result = await register_document(
        title=payload.title or payload.file_name,
        file_base64=payload.file_base64,
        signature=payload.signature,
        participant_count=len(payload.participant_user_ids),
        session=session,
        o_doc_id=doc.id
    )

    if not registration_result["success"]:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Document registration failed: {registration_result['error']}")

    doc.file_path = registration_result["file_path"]
    doc.s_id = registration_result["document_id"]
    await session.commit()

    return {"document_id": doc.id}