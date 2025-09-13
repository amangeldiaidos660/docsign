from fastapi import APIRouter, Depends, HTTPException, Cookie, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import SessionLocal
from db.models import Document, User, DocumentParticipant
from services.signature_service import add_signature
from services.pdf_signature_service import PDFSignatureService
from services.participant_status_update_service import update_participants_status

router = APIRouter(prefix="/sign", tags=["sign"])

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@router.get("/getbase64")
async def get_base64(
    document_id: int = Query(...),
    uid: int | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
):
    if uid is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    res = await session.execute(select(Document).where(Document.id == document_id))
    doc = res.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    return {"document_id": doc.id, "file_base64": doc.file_base64}


class AddSignPayload(BaseModel):
    document_id: int
    file_base64: str
    signature: str

@router.post("/addsign")
async def add_sign(
    payload: AddSignPayload,
    uid: int | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
):
    if uid is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    
    res = await session.execute(select(Document).where(Document.id == payload.document_id))
    doc = res.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    if not getattr(doc, "s_id", None):
        raise HTTPException(status_code=400, detail="document has no external id")
    
    service_result = await add_signature(doc.s_id, payload.signature)
    
    
    if "signature_details" in service_result and doc.file_path:
        signature_details = service_result["signature_details"]
        
        participants_res = await session.execute(
            select(DocumentParticipant, User).join(User, DocumentParticipant.user_id == User.id)
            .where(DocumentParticipant.document_id == payload.document_id)
        )
        participants_data = participants_res.all()
        
        signed_iins = {user.iin for participant, user in participants_data if participant.status == "signed"}
        
        filtered_signatures = [
            sig for sig in signature_details["signatures"] 
            if sig.get("iin") and sig["iin"] not in signed_iins
        ]
        
        if filtered_signatures:
            filtered_signature_details = {
                "total_signatures": len(filtered_signatures),
                "signatures": filtered_signatures
            }
            print("filtered_signature_details", filtered_signature_details)
            pdf_service = PDFSignatureService()
            await pdf_service.add_signature_page(doc.file_path, filtered_signature_details)

            await update_participants_status(
                session=session,
                o_doc_id=payload.document_id,
                signature_data=filtered_signature_details
            )
    
    return {"document_id": doc.id}