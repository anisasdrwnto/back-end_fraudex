from sqlalchemy import Sequence, select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole

user_id_seq = Sequence("user_id_seq")


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_by_id(db: Session, id_user: str) -> User | None:
    return db.get(User, id_user)


def create(
    db: Session,
    *,
    nama: str,
    email: str,
    password_hash: str,
    role: UserRole = UserRole.user,
) -> User:
    n = db.execute(user_id_seq.next_value()).scalar_one()
    user = User(
        id_user=f"USR{n:02d}",
        nama=nama,
        email=email.lower(),
        password=password_hash,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user