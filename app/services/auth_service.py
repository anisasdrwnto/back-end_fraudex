from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
    except IntegrityError:  # dua request dengan email sama persis bersamaan
        db.rollback()
        raise HTTPException(status_code=409, detail="Email sudah terdaftar.")


def authenticate(db: Session, email: str, password: str) -> TokenResponse:
    user = user_repo.get_by_email(db, email)
    if user is None or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Email atau kata sandi salah.")
    return _token_response(user)


def refresh(db: Session, refresh_token: str) -> TokenResponse:
    id_user = decode_token(refresh_token, "refresh")
    user = user_repo.get_by_id(db, id_user) if id_user else None
    if user is None:
        raise HTTPException(status_code=401, detail="Refresh token tidak valid.")
    return _token_response(user)