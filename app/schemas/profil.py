import re

from pydantic import BaseModel, Field, field_validator


class ProfilOut(BaseModel):
    id_user: str
    name: str
    email: str
    role: str
    foto_url: str | None = None
    no_telepon: str | None = None
    has_password: bool = True


class ProfilUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    no_telepon: str | None = Field(default=None, max_length=20)

    @field_validator("no_telepon")
    @classmethod
    def cek_telepon(cls, v: str | None) -> str | None:
        if v is None or v.strip() == "":
            return None
        v = v.strip()
        if not re.fullmatch(r"\+?[0-9]{8,15}", v):
            raise ValueError("Nomor telepon tidak valid")
        return v


class PasswordUpdate(BaseModel):
    # null untuk akun Google yang baru membuat kata sandi pertama
    current_password: str | None = Field(default=None, max_length=64)
    new_password: str = Field(min_length=8, max_length=64)