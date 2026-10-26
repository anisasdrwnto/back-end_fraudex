from sqlalchemy import Sequence, select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole

user_id_seq = Sequence("user_id_seq")


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_by_id(db: Session, id_user: str) -> User | None:
    return db.get(User, id_user)


def get_by_google_sub(db: Session, google_sub: str) -> User | None:
    return db.scalar(select(User).where(User.google_sub == google_sub))


def create(
    db: Session,
    *,
    nama: str,
    email: str,
    password_hash: str | None,
    role: UserRole = UserRole.user,
    google_sub: str | None = None,
) -> User:
    n = db.execute(user_id_seq.next_value()).scalar_one()
    user = User(
        id_user=f"USR{n:02d}",
        nama=nama,
        email=email.lower(),
        password=password_hash,
        google_sub=google_sub,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user