from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Risiko = Literal["aman", "waspada", "berbahaya"]


class PrediksiIn(BaseModel):
    teks: str = Field(min_length=1, max_length=2000)


class PrediksiOut(BaseModel):
    id_deteksi: str
    tingkat_risiko: Risiko
    skor_kepercayaan: float
    kata_highlight: list[str]


class RiwayatItem(BaseModel):
    id_deteksi: str
    isi_pesan: str
    tingkat_risiko: Risiko
    skor_kepercayaan: float
    kata_highlight: list[str]
    tanggal_deteksi: datetime