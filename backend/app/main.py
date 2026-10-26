from datetime import datetime
from app.db import query
from fastapi import FastAPI
from dataclasses import asdict
from app.operations.summary import summary_stats


app = FastAPI(title="CAISO Assistant API")


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

@app.get("/api/analyze/summary")
def api_summary(node_id: str, market: str, start: datetime, end: datetime):
    return asdict(summary_stats(node_id, market, start, end))
