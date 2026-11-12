"""tambah foto_url dan no_telepon ke users

Revision ID: 4d2e9a7c1b38
Revises: 6981bfd9cc64
Create Date: 2026-11-09
"""
from typing import Sequence, Union

from alembic import op

revision: str = "4d2e9a7c1b38"
down_revision: Union[str, Sequence[str], None] = "6981bfd9cc64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS: aman walaupun kolom foto_url sudah dibuat manual di Neon
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS foto_profil VARCHAR(500)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS no_telepon VARCHAR(20)")


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS no_telepon")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS foto_profil")
