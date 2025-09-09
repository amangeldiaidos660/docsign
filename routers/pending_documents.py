from fastapi import APIRouter, Depends, Cookie, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import SessionLocal
from services.document_service import get_pending_documents
from typing import Dict, List, Any

router = APIRouter(prefix="/documents/pending", tags=["documents"])

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@router.get("")
async def get_pending(
    uid: int | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session)
):
    if not uid:
        raise HTTPException(status_code=401, detail="unauthorized")
    
    documents = await get_pending_documents(session, uid)
    return {"documents": documents}