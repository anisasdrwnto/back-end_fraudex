from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AdminStats(BaseModel):
    total_users: int
    total_sms: int
    aman: int
    waspada: int
    berbahaya: int


class UserAdminOut(BaseModel):
    id_user: str
    nama: str
    email: str
    role: str
    created_at: datetime


class UserAdminUpdate(BaseModel):
    nama: str = Field(min_length=2, max_length=100)
    role: Literal["user", "admin"]


class FeedbackAdminOut(BaseModel):
    id_feedback: str
    nama_user: str
    rating: int | None
    catatan_feedback: str | None
    tanggapan_admin: str | None
    status: str
    tanggal_feedback: datetime


class FeedbackAdminUpdate(BaseModel):
    status: Literal["menunggu", "ditinjau", "ditindaklanjuti"]
    tanggapan_admin: str | None = Field(default=None, max_length=1000)