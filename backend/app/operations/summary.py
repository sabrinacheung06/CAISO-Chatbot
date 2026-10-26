from datetime import datetime

from app.db import query

from .base import Result

SQL = """
    SELECT COUNT(*)            AS n_intervals,
           AVG(lmp)            AS mean_lmp,
           MIN(lmp)            AS min_lmp,
           MAX(lmp)            AS max_lmp,
           STDDEV_SAMP(lmp)    AS std_lmp,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY lmp) AS median_lmp,
           MIN(ts_utc)         AS first_ts,
           MAX(ts_utc)         AS last_ts
    FROM lmp
    WHERE node_id = %(node_id)s
      AND market  = %(market)s
      AND ts_utc >= %(start)s
      AND ts_utc <  %(end)s
"""


def summary_stats(node_id: str, market: str,
                  start: datetime, end: datetime) -> Result:
    params = {"node_id": node_id, "market": market,
              "start": start, "end": end}
    row = query(SQL, params)[0]

    values = {k: (float(v) if isinstance(v, (int, float)) or hasattr(v, "quantize")
                  else v)
              for k, v in row.items()}
    values["n_intervals"] = int(row["n_intervals"])

    return Result(
        op="summary_stats",
        params={"node_id": node_id, "market": market,
                "start": start.isoformat(), "end": end.isoformat()},
        source={"table": "lmp", "node_id": node_id, "market": market},
        interval=(start, end),
        values=values,
        method=("Count, mean, min, max, sample standard deviation and median "
                "of the LMP over all intervals in the range "
                "(start inclusive, end exclusive)."),
        sql=SQL.strip(),
    )