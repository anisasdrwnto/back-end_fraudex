from alembic import context

from app.core.database import Base, engine
from app.models import user  # noqa: F401  (mendaftarkan model ke Base)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()