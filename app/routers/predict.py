from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.repositories import deteksi_repo
from app.schemas.predict import PrediksiIn, PrediksiOut, RiwayatItem
from app.services.ml_service import analisis

router = APIRouter(tags=["deteksi"])


@router.post("/predict", response_model=PrediksiOut)
@limiter.limit("30/minute")
def predict(
    request: Request,  # wajib ada untuk slowapi
    body: PrediksiIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    hasil = analisis(body.teks)
    deteksi = deteksi_repo.simpan_hasil(db, user.id_user, body.teks, hasil)
    return {"id_deteksi": deteksi.id_deteksi, **hasil}


@router.get("/riwayat", response_model=list[RiwayatItem])
def riwayat(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    baris = deteksi_repo.daftar_riwayat(db, user.id_user, limit, offset)
    return [
        RiwayatItem(
            id_deteksi=d.id_deteksi,
            isi_pesan=isi,
            tingkat_risiko=d.tingkat_risiko.value,
            skor_kepercayaan=d.skor_kepercayaan,
            kata_highlight=d.kata_highlight,
            tanggal_deteksi=d.tanggal_deteksi,
        )
        for d, isi in baris
    ]