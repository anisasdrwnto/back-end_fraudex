from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.feedback import Feedback, StatusFeedback
from app.models.histori_deteksi import HistoriDeteksi
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminStats,
    FeedbackAdminOut,
    FeedbackAdminUpdate,
    UserAdminOut,
    UserAdminUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ----------------------------------------------------------- statistik
@router.get("/stats", response_model=AdminStats)
def statistik(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    baris = db.execute(
        select(HistoriDeteksi.tingkat_risiko, func.count())
        .group_by(HistoriDeteksi.tingkat_risiko)
    ).all()
    hitung = {r.value: n for r, n in baris}
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    aman = hitung.get("aman", 0)
    waspada = hitung.get("waspada", 0)
    berbahaya = hitung.get("berbahaya", 0)
    return AdminStats(
        total_users=total_users,
        total_sms=aman + waspada + berbahaya,
        aman=aman,
        waspada=waspada,
        berbahaya=berbahaya,
    )


# ------------------------------------------------------------ pengguna
def _user_out(u: User) -> UserAdminOut:
    return UserAdminOut(
        id_user=u.id_user,
        nama=u.nama,
        email=u.email,
        role=u.role.value,
        created_at=u.created_at,
    )


@router.get("/users", response_model=list[UserAdminOut])
def daftar_user(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    users = db.scalars(select(User).order_by(User.created_at)).all()
    return [_user_out(u) for u in users]


@router.put("/users/{id_user}", response_model=UserAdminOut)
def ubah_user(
    id_user: str,
    body: UserAdminUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    u = db.get(User, id_user)
    if u is None:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan.")
    if u.id_user == admin.id_user and body.role != "admin":
        raise HTTPException(
            status_code=400, detail="Anda tidak bisa menurunkan role akun sendiri."
        )
    u.nama = body.nama.strip()
    u.role = UserRole(body.role)
    db.commit()
    db.refresh(u)
    return _user_out(u)


@router.delete("/users/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_user(
    id_user: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    u = db.get(User, id_user)
    if u is None:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan.")
    if u.id_user == admin.id_user:
        raise HTTPException(status_code=400, detail="Anda tidak bisa menghapus akun sendiri.")
    try:
        db.delete(u)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Pengguna tidak bisa dihapus karena masih punya data terkait."
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------ feedback
def _fb_out(fb: Feedback, nama: str) -> FeedbackAdminOut:
    return FeedbackAdminOut(
        id_feedback=fb.id_feedback,
        nama_user=nama,
        rating=fb.rating,
        catatan_feedback=fb.catatan_feedback,
        tanggapan_admin=fb.tanggapan_admin,
        status=fb.status.value,
        tanggal_feedback=fb.tanggal_feedback,
    )


@router.get("/feedback", response_model=list[FeedbackAdminOut])
def daftar_feedback(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    baris = db.execute(
        select(Feedback, User.nama)
        .join(User, User.id_user == Feedback.id_user)
        .order_by(Feedback.tanggal_feedback.desc())
    ).all()
    return [_fb_out(fb, nama) for fb, nama in baris]


@router.put("/feedback/{id_feedback}", response_model=FeedbackAdminOut)
def ubah_feedback(
    id_feedback: str,
    body: FeedbackAdminUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    fb = db.get(Feedback, id_feedback)
    if fb is None:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan.")
    fb.status = StatusFeedback(body.status)
    tanggapan = (body.tanggapan_admin or "").strip()
    fb.tanggapan_admin = tanggapan or None
    db.commit()
    db.refresh(fb)
    nama = db.scalar(select(User.nama).where(User.id_user == fb.id_user)) or "-"
    return _fb_out(fb, nama)


@router.delete("/feedback/{id_feedback}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_feedback(
    id_feedback: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    fb = db.get(Feedback, id_feedback)
    if fb is None:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan.")
    db.delete(fb)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)