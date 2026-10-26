import enum
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StatusFeedback(str, enum.Enum):  # GANTI nilainya sesuai SKPL 
    menunggu = "menunggu"
    ditinjau = "ditinjau"
    ditindaklanjuti = "ditindaklanjuti"
   


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint(
            "rating IS NULL OR rating BETWEEN 1 AND 5", name="ck_feedback_rating"
        ),
    )

    id_feedback: Mapped[str] = mapped_column(String(30), primary_key=True)  # FB01, FB02, ...
    id_deteksi: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("histori_deteksi.id_deteksi", ondelete="CASCADE"),
        index=True,
    )
    id_user: Mapped[str] = mapped_column(
        String(30), ForeignKey("users.id_user", ondelete="CASCADE"), index=True
    )
    catatan_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusFeedback] = mapped_column(
        Enum(StatusFeedback, name="status_feedback"),
        default=StatusFeedback.menunggu,
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tanggal_feedback: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )