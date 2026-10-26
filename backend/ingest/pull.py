import hashlib
import time
from pathlib import Path

import pandas as pd
from gridstatus import CAISO, Markets

RAW_DIR = Path("data/raw")   # relative to backend/ when you run from there
MARKETS = {
    "DAM": Markets.DAY_AHEAD_HOURLY,
    "FMM": Markets.REAL_TIME_15_MIN,
    "RTD": Markets.REAL_TIME_5_MIN
}


def month_chunks(start: str, end: str):
    """Yield (chunk_start, chunk_end) per calendar month; `end` is exclusive."""
    cur, stop = pd.Timestamp(start), pd.Timestamp(end)
    while cur < stop:
        nxt = min(cur + pd.offsets.MonthBegin(1), stop)
        yield cur, nxt
        cur = nxt


def _cache_path(label, start, end, nodes):
    key = hashlib.md5(",".join(sorted(nodes)).encode()).hexdigest()[:8]
    return RAW_DIR / f"{label}_{start:%Y%m%d}_{end:%Y%m%d}_{key}.parquet"


def fetch_chunk(caiso, label, start, end, nodes, retries=3):
    """Return a raw DataFrame for one chunk, or None if all attempts failed."""
    path = _cache_path(label, start, end, nodes)
    if path.exists():
        print(f"  cache hit: {path.name}")
        return pd.read_parquet(path)

    for attempt in range(1, retries + 1):
        try:
            df = caiso.get_lmp(
                date=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                market=MARKETS[label],
                locations=nodes,
                sleep=5,
                verbose=False,
            )
            if df.empty:
                raise ValueError("CAISO returned no rows")
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            df.to_parquet(path, index=False)
            return df
        except Exception as e:
            print(f"  attempt {attempt}/{retries} failed: {e}")
            time.sleep(10 * attempt)
    return None