from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.profil import PasswordUpdate, ProfilOut, ProfilUpdate
from app.services import cloudinary_service

router = APIRouter(prefix="/profil", tags=["profil"])

MAKS_FOTO = 3 * 1024 * 1024  # 3 MB


def _format_gambar(data: bytes) -> str | None:
    """Cek jenis file dari isinya (bukan dari nama/header yang bisa dipalsukan)."""
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def _out(u: User) -> ProfilOut:
    return ProfilOut(
        id_user=u.id_user,
        name=u.nama,
        email=u.email,
        role=u.role.value,
        foto_url=u.foto_url,
        no_telepon=u.no_telepon,
        has_password=bool(u.password),
    )


@router.get("", response_model=ProfilOut)
def lihat_profil(user: User = Depends(get_current_user)):
    return _out(user)


@router.put("", response_model=ProfilOut)
def ubah_profil(
    body: ProfilUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.nama = body.name.strip()
    user.no_telepon = body.no_telepon
    db.commit()
    db.refresh(user)
    return _out(user)


@router.put("/password")
@limiter.limit("5/minute")  # cegah tebak-tebak kata sandi lama
def ubah_password(
    request: Request,  # wajib ada untuk slowapi
    body: PasswordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.password:
        # Akun email+password: wajib membuktikan kata sandi lama
        if not body.current_password or not verify_password(body.current_password, user.password):
            raise HTTPException(status_code=400, detail="Kata sandi lama salah.")
        if verify_password(body.new_password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Kata sandi baru tidak boleh sama dengan yang lama.",
            )
    # Akun Google (password kosong): boleh langsung membuat kata sandi pertama
    user.password = hash_password(body.new_password)
    db.commit()
    return {"message": "Kata sandi berhasil diperbarui."}


@router.post("/foto", response_model=ProfilOut)
async def unggah_foto(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    if len(data) > MAKS_FOTO:
        raise HTTPException(status_code=413, detail="Ukuran foto maksimal 3 MB.")
    if _format_gambar(data) is None:
        raise HTTPException(status_code=415, detail="Format foto harus JPG, PNG, atau WEBP.")
    try:
        url = await run_in_threadpool(
            cloudinary_service.upload_foto_profil, data, user.id_user
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Gagal mengunggah foto. Coba lagi.")
    user.foto_url = url
    db.commit()
    db.refresh(user)
    return _out(user)
