from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.feedback import Feedback, StatusFeedback
from app.models.histori_deteksi import HistoriDeteksi
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _id_baru(db: Session) -> str:
    """FB01, FB02, ... (lanjut dari nomor terbesar yang ada)."""
    ids = db.scalars(select(Feedback.id_feedback)).all()
    nomor = [int(i[2:]) for i in ids if i.startswith("FB") and i[2:].isdigit()]
    return f"FB{max(nomor, default=0) + 1:02d}"


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def kirim_feedback(
    body: FeedbackCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.id_deteksi is not None:
        deteksi = db.get(HistoriDeteksi, body.id_deteksi)
        # Sama-sama "tidak ditemukan" agar tidak membocorkan ID milik orang lain.
        if deteksi is None or deteksi.id_user != user.id_user:
            raise HTTPException(status_code=404, detail="Riwayat SMS tidak ditemukan.")

    fb = Feedback(
        id_feedback=_id_baru(db),
        id_user=user.id_user,
        id_deteksi=body.id_deteksi,
        catatan_feedback=body.catatan_feedback,
        rating=body.rating,
        status=StatusFeedback.menunggu,
        tanggal_feedback=datetime.now(timezone.utc),
        boleh_dihubungi=body.boleh_dihubungi,
        gabung_riset=body.gabung_riset,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return FeedbackOut(
        id_feedback=fb.id_feedback,
        rating=fb.rating,
        id_deteksi=fb.id_deteksi,
        catatan_feedback=fb.catatan_feedback,
        status=fb.status.value,
        tanggal_feedback=fb.tanggal_feedback,
        boleh_dihubungi=fb.boleh_dihubungi,
        gabung_riset=fb.gabung_riset,
    )