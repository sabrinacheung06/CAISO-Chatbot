import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DB_URL = os.getenv("DATABASE_URL",
                   "postgresql://caiso:caiso_dev@localhost:5432/caiso")


def query(sql: str, params: dict | None = None) -> list[dict]:
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        return conn.execute(sql, params).fetchall()