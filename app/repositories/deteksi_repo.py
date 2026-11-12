from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.ids import id_berikutnya
from app.models.histori_deteksi import HistoriDeteksi, TingkatRisiko
from app.models.pesan_sms import PesanSms


def simpan_hasil(db: Session, id_user: str, teks: str, hasil: dict) -> HistoriDeteksi:
    sms = PesanSms(
        id_sms=id_berikutnya(db, "seq_pesan_sms", "PS"),
        id_user=id_user,
        isi_pesan=teks,
    )
    db.add(sms)
    db.flush()  # sms harus ada dulu sebelum dirujuk oleh deteksi

    deteksi = HistoriDeteksi(
        id_deteksi=id_berikutnya(db, "seq_histori_deteksi", "DT"),
        id_sms=sms.id_sms,
        id_user=id_user,
        tingkat_risiko=TingkatRisiko(hasil["tingkat_risiko"]),
        skor_kepercayaan=hasil["skor_kepercayaan"],
        kata_highlight=hasil["kata_highlight"],
    )
    db.add(deteksi)
    db.commit()
    db.refresh(deteksi)
    return deteksi


def daftar_riwayat(db: Session, id_user: str, limit: int = 20, offset: int = 0):
    stmt = (
        select(HistoriDeteksi, PesanSms.isi_pesan)
        .join(PesanSms, PesanSms.id_sms == HistoriDeteksi.id_sms)
        .where(HistoriDeteksi.id_user == id_user)
        .order_by(HistoriDeteksi.tanggal_deteksi.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).all()