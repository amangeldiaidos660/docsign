from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Integer, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

def get_current_time():
    return datetime.utcnow()

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("iin", name="uq_users_iin"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    iin: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    bin: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_current_time, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_current_time, onupdate=get_current_time, nullable=False)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_base64: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_current_time, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_current_time, onupdate=get_current_time, nullable=False)

    owner: Mapped["User"] = relationship("User")
    participants: Mapped[list["DocumentParticipant"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentParticipant(Base):
    __tablename__ = "document_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # initiator | signer
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")  # pending | signed
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="participants")
