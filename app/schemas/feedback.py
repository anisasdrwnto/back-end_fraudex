from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    id_deteksi: str | None = Field(default=None, max_length=30)
    catatan_feedback: str | None = Field(default=None, max_length=1000)
    boleh_dihubungi: bool = False
    gabung_riset: bool = False

    @field_validator("catatan_feedback", "id_deteksi")
    @classmethod
    def kosong_jadi_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None


class FeedbackOut(BaseModel):
    id_feedback: str
    rating: int | None
    id_deteksi: str | None
    catatan_feedback: str | None
    status: str
    tanggal_feedback: datetime
    boleh_dihubungi: bool
    gabung_riset: bool