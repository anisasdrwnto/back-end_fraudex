from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PesanSms(Base):
    __tablename__ = "pesan_sms"

    id_sms: Mapped[str] = mapped_column(String(30), primary_key=True)  # PS01, PS02, ...
    id_user: Mapped[str] = mapped_column(
        String(30), ForeignKey("users.id_user", ondelete="CASCADE"), index=True
    )
    isi_pesan: Mapped[str] = mapped_column(Text)
    tanggal_cek: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )