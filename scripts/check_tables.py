from sqlalchemy import inspect

from app.core.database import engine

insp = inspect(engine)
print("Tabel:", insp.get_table_names())
for col in insp.get_columns("users"):
       print(" -", col["name"], col["type"].compile(dialect=engine.dialect))