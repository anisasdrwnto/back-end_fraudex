import io
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader

from app.core.config import settings

_configured = False


def _configure() -> None:
    """CLOUDINARY_URL berbentuk cloudinary://API_KEY:API_SECRET@CLOUD_NAME"""
    global _configured
    if _configured:
        return
    u = urlparse(settings.CLOUDINARY_URL)
    if not (u.hostname and u.username and u.password):
        raise RuntimeError("CLOUDINARY_URL belum diisi dengan benar di .env")
    cloudinary.config(
        cloud_name=u.hostname,
        api_key=u.username,
        api_secret=u.password,
        secure=True,
    )
    _configured = True


def upload_foto_profil(data: bytes, id_user: str) -> str:
    """Unggah foto ke folder fraudex/profil dan kembalikan URL https-nya.
    public_id = id_user, jadi foto lama otomatis tertimpa (tidak menumpuk)."""
    _configure()
    hasil = cloudinary.uploader.upload(
        io.BytesIO(data),
        folder="fraudex/profil",
        public_id=id_user,
        overwrite=True,
        invalidate=True,
        resource_type="image",
        transformation=[{"width": 800, "height": 800, "crop": "limit"}],
    )
    return hasil["secure_url"]
