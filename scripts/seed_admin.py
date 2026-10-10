from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import UserRole
from app.repositories import user_repo

if not (settings.ADMIN_NAME and settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD):
    raise SystemExit("Isi ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD di .env dulu.")

with SessionLocal() as db:
    if user_repo.get_by_email(db, settings.ADMIN_EMAIL):
        print("Admin sudah ada, dilewati.")
    else:
        u = user_repo.create(
            db,
            nama=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        print("Admin dibuat:", u.id_user, u.email)