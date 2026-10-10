from sqlalchemy import text

from app.core.database import engine

with engine.connect() as conn:
    print("Terhubung ke:", conn.execute(text("SELECT current_database()")).scalar())
    print(conn.execute(text("SELECT version()")).scalar())