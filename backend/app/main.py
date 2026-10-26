import os
from datetime import datetime

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://caiso:caiso_dev@localhost:5432/caiso",
)

app = FastAPI(title="CAISO Assistant API")


def query(sql: str, params: dict | None = None) -> list[dict]:
    """Run a SQL query and return rows as a list of dictionaries."""
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        return conn.execute(sql, params).fetchall()


@app.get("/api/health")
def health():
    return {"status": "ok", "db": query("SELECT 1 AS ok")[0]["ok"]}


@app.get("/api/nodes")
def list_nodes():
    return query("SELECT node_id, node_type FROM node ORDER BY node_id")


@app.get("/api/lmp")
def get_lmp(node_id: str, market: str, start: datetime, end: datetime,
            limit: int = 1000):
    sql = """
        SELECT ts_utc, lmp, energy, congestion, loss
        FROM lmp
        WHERE node_id = %(node_id)s AND market = %(market)s
          AND ts_utc >= %(start)s AND ts_utc < %(end)s
        ORDER BY ts_utc
        LIMIT %(limit)s
    """
    return query(sql, {"node_id": node_id, "market": market,
                       "start": start, "end": end, "limit": limit})
