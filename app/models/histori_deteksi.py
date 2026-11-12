import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TingkatRisiko(str, enum.Enum):
    aman = "aman"
    waspada = "waspada"
    berbahaya = "berbahaya"


class HistoriDeteksi(Base):
    __tablename__ = "histori_deteksi"

    id_deteksi: Mapped[str] = mapped_column(String(30), primary_key=True)  # DT01, DT02, ...
    id_sms: Mapped[str] = mapped_column(
        String(30), ForeignKey("pesan_sms.id_sms", ondelete="CASCADE"), index=True
    )
    id_user: Mapped[str] = mapped_column(
        String(30), ForeignKey("users.id_user", ondelete="CASCADE"), index=True
    )
    tingkat_risiko: Mapped[TingkatRisiko] = mapped_column(
        Enum(TingkatRisiko, name="tingkat_risiko")
    )
    skor_kepercayaan: Mapped[float] = mapped_column(Float)
    kata_highlight: Mapped[list] = mapped_column(JSONB, default=list)
    tanggal_deteksi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )