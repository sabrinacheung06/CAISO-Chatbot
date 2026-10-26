import os

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

load_dotenv()
DB_URL = os.getenv("DATABASE_URL",
                   "postgresql://caiso:caiso_dev@localhost:5432/caiso")
COLS = ["ts_utc", "market", "node_id", "lmp", "energy", "congestion", "loss", "ghg"]


def load_chunk(df, source: str, params: dict) -> int:
    """Insert one chunk. Safe to rerun. Returns the number of NEW rows."""
    df = df.astype(object).where(df.notna(), None)   # NaN -> NULL
    nodes = df[["node_id", "node_type"]].drop_duplicates("node_id")
    rows = df[COLS].itertuples(index=False, name=None)

    with psycopg.connect(DB_URL) as conn:          # commits on success
        ingest_id = conn.execute(
            "INSERT INTO ingest_log (source_url, query_params) "
            "VALUES (%s, %s) RETURNING id",
            (source, Jsonb(params)),
        ).fetchone()[0]

        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO node (node_id, node_type) VALUES (%s, %s) "
                "ON CONFLICT DO NOTHING",
                nodes.itertuples(index=False, name=None),
            )
            cur.executemany(
                "INSERT INTO lmp (ts_utc, market, node_id, lmp, energy, "
                "congestion, loss, ghg, ingest_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                [(*r, ingest_id) for r in rows],
            )

        inserted = conn.execute(
            "SELECT COUNT(*) FROM lmp WHERE ingest_id = %s", (ingest_id,)
        ).fetchone()[0]
        conn.execute("UPDATE ingest_log SET row_count = %s WHERE id = %s",
                     (inserted, ingest_id))
    return inserted