from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User, Document, DocumentParticipant
from datetime import datetime

async def update_participants_status(
    session: AsyncSession,
    o_doc_id: int,
    signature_data: Dict[str, Any]
) -> None:

    signed_data = {}
    for sig in signature_data.get("signatures", []):
        if sig.get("iin") and sig.get("signed_at"):
            signed_data[sig["iin"]] = datetime.strptime(
                sig["signed_at"], 
                "%d.%m.%Y %H:%M:%S"
            )

    if not signed_data:
        return

    
    users_stmt = select(User).where(User.iin.in_(list(signed_data.keys())))
    users_result = await session.execute(users_stmt)
    users = users_result.scalars().all()
    
    if not users:
        return
        
    
    user_sign_times = {
        user.id: signed_data[user.iin] 
        for user in users
    }

    participants_stmt = select(DocumentParticipant).where(
        DocumentParticipant.document_id == o_doc_id,
        DocumentParticipant.user_id.in_(list(user_sign_times.keys()))
    )
    
    participants_result = await session.execute(participants_stmt)
    participants = participants_result.scalars().all()
    
    
    updates_count = 0
    for participant in participants:
        signed_at = user_sign_times[participant.user_id]
        participant.status = "signed"
        participant.signed_at = signed_at
        updates_count += 1

    if updates_count > 0:
        await session.commit()
