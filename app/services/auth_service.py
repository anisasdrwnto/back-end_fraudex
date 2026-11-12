from fastapi import HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories import user_repo
from app.schemas.auth import RegisterRequest, TokenResponse

_google_request = google_requests.Request()


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id_user),
        refresh_token=create_refresh_token(user.id_user),
        name=user.nama,
        role=user.role.value,
        email=user.email,
    )


def register(db: Session, body: RegisterRequest) -> None:
    if user_repo.get_by_email(db, body.email):
        raise HTTPException(status_code=409, detail="Email sudah terdaftar.")
    try:
        user_repo.create(
            db,
            nama=body.name.strip(),
            email=body.email,
            password_hash=hash_password(body.password),
            role=UserRole.user,  # register publik SELALU jadi user biasa
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email sudah terdaftar.")


def authenticate(db: Session, email: str, password: str) -> TokenResponse:
    user = user_repo.get_by_email(db, email)
    # Akun yang dibuat lewat Google tidak punya password, jadi tidak bisa login di sini
    if user is None or not user.password or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Email atau kata sandi salah.")
    return _token_response(user)


def refresh(db: Session, refresh_token: str) -> TokenResponse:
    id_user = decode_token(refresh_token, "refresh")
    user = user_repo.get_by_id(db, id_user) if id_user else None
    if user is None:
        raise HTTPException(status_code=401, detail="Refresh token tidak valid.")
    return _token_response(user)


def _verify_google_token(credential: str) -> dict:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Login Google belum dikonfigurasi.")
    try:
        # Memeriksa tanda tangan, masa berlaku, penerbit, dan audience (Client ID kita)
        info = google_id_token.verify_oauth2_token(
            credential,
            _google_request,
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )
    except ValueError as e:
        print("GOOGLE VERIFY ERROR:", e, flush=True)
        raise HTTPException(status_code=401, detail="Token Google tidak valid.")
    if not info.get("email") or not info.get("email_verified"):
        raise HTTPException(status_code=401, detail="Email Google belum terverifikasi.")
    return info


def google_login(db: Session, credential: str) -> TokenResponse:
    info = _verify_google_token(credential)
    sub = info["sub"]  # ID unik akun Google ini, selalu sama untuk orang yang sama
    email = info["email"].lower()
    nama = (info.get("name") or email.split("@")[0]).strip()[:100]

    # 1. Akun Google ini sudah pernah masuk: langsung login
    user = user_repo.get_by_google_sub(db, sub)
    if user is not None:
        return _token_response(user)

    # 2. Email sudah dipakai akun email+password: jangan digabung otomatis
    if user_repo.get_by_email(db, email) is not None:
        raise HTTPException(
            status_code=409,
            detail="Email ini sudah terdaftar dengan kata sandi. Silakan masuk dengan email dan kata sandi.",
        )

    # 3. Akun baru: satu baris baru per akun Google, selalu role user
    try:
        user = user_repo.create(
            db,
            nama=nama,
            email=email,
            password_hash=None,
            role=UserRole.user,
            google_sub=sub,
        )
    except IntegrityError:  # dua klik bersamaan dari akun yang sama
        db.rollback()
        user = user_repo.get_by_google_sub(db, sub)
        if user is None:
            raise HTTPException(status_code=409, detail="Gagal membuat akun, coba lagi.")
    return _token_response(user)