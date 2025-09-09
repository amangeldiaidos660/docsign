from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Document, DocumentParticipant, User
from typing import List, Dict, Any

async def get_pending_documents(session: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
    stmt = (
        select(Document, DocumentParticipant, User)
        .join(DocumentParticipant, Document.id == DocumentParticipant.document_id)
        .join(User, Document.owner_id == User.id)
        .where(
            DocumentParticipant.user_id == user_id,
            DocumentParticipant.status == "pending",
            Document.status != "cancelled"
        )
        .order_by(Document.created_at.desc())
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    docs = []
    for doc, participant, owner in rows:
        all_participants = await session.execute(
            select(DocumentParticipant, User)
            .join(User, DocumentParticipant.user_id == User.id)
            .where(DocumentParticipant.document_id == doc.id)
        )
        
        parties = []
        for part, user in all_participants:
            parties.append({
                "role": part.role,
                "status": part.status,
                "signed_at": part.signed_at.isoformat() if part.signed_at else None,
                "full_name": user.full_name,
                "organization": user.organization,
                "bin": user.bin,
                "iin": user.iin,
                "email": user.email
            })
            
        docs.append({
            "id": doc.id,
            "title": doc.title or doc.file_name,
            "created_at": doc.created_at.isoformat(),
            "status": doc.status,
            "file_path": doc.file_path,
            "parties": parties,
            "initiator": {
                "full_name": owner.full_name,
                "organization": owner.organization,
                "bin": owner.bin,
                "iin": owner.iin,
                "email": owner.email
            }
        })
        
    return docs


async def get_signed_documents(session: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
    stmt = (
        select(Document, DocumentParticipant, User)
        .join(DocumentParticipant, Document.id == DocumentParticipant.document_id)
        .join(User, Document.owner_id == User.id)
        .where(
            DocumentParticipant.user_id == user_id,
            DocumentParticipant.status == "signed",
            Document.status != "cancelled"
        )
        .order_by(Document.created_at.desc())
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    docs = []
    for doc, participant, owner in rows:
        all_participants = await session.execute(
            select(DocumentParticipant, User)
            .join(User, DocumentParticipant.user_id == User.id)
            .where(DocumentParticipant.document_id == doc.id)
        )
        
        parties = []
        for part, user in all_participants:
            parties.append({
                "role": part.role,
                "status": part.status,
                "signed_at": part.signed_at.isoformat() if part.signed_at else None,
                "full_name": user.full_name,
                "organization": user.organization,
                "bin": user.bin,
                "iin": user.iin,
                "email": user.email
            })
            
        docs.append({
            "id": doc.id,
            "created_at": doc.created_at.isoformat(),
            "file_path": doc.file_path,
            "parties": parties,
            "status": doc.status
        })
        
    return docs