from fastapi import APIRouter, Depends, HTTPException, Cookie, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import SessionLocal
from db.models import Document

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
):
    if uid is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    fb_len = len(payload.file_base64 or "")
    sig_len = len(payload.signature or "")
    print(f"[addsign] uid={uid}, document_id={payload.document_id}, file_base64_len={fb_len}, signature_len={sig_len}")
    return {
        "ok": True,
        "uid": uid,
        "document_id": payload.document_id,
        "file_base64_len": fb_len,
        "signature_len": sig_len
    }