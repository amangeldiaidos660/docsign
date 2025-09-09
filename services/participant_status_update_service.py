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
    print(f"\nОбновление статусов для документа {o_doc_id}")
    
    # Получаем ИИНы подписавших
    signed_iins = []
    for sig in signature_data["signatures"]:
        if sig.get("iin"):
            signed_iins.append(sig["iin"])
            print(f"Найдена подпись от пользователя с ИИН: {sig['iin']}")

    if not signed_iins:
        print("Нет подписей с ИИН")
        return

    # Правильный запрос с учетом связей моделей
    stmt = (
        select(DocumentParticipant)
        .join(Document, Document.id == DocumentParticipant.document_id)
        .join(User, User.id == DocumentParticipant.user_id)
        .where(
            DocumentParticipant.document_id == o_doc_id,
            User.iin.in_(signed_iins)
        )
    )
    
    result = await session.execute(stmt)
    participants = result.scalars().all()
    
    print(f"Найдено участников: {len(participants)}")
    
    # Обновляем статусы
    updates_count = 0
    for participant in participants:
        print(f"Обновление статуса участника {participant.user_id}")
        participant.status = "signed"
        participant.signed_at = datetime.utcnow()
        updates_count += 1
    
    if updates_count > 0:
        await session.commit()
        print(f"Обновлено статусов: {updates_count}")
    else:
        print("Нет обновлений статусов")