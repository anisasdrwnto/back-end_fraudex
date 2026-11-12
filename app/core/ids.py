from sqlalchemy import Sequence, select
from sqlalchemy.orm import Session


def id_berikutnya(db: Session, nama_seq: str, prefix: str) -> str:
    """Contoh: PS01, PS02, ... PS99, PS100 (otomatis melebar kalau lewat 99)."""
    n = db.execute(select(Sequence(nama_seq).next_value())).scalar_one()
    return f"{prefix}{n:02d}"