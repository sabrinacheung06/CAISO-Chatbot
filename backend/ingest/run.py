import argparse

from gridstatus import CAISO

from .load import load_chunk
from .pull import fetch_chunk, month_chunks
from .transform import to_lmp_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--market", required=True, choices=["DAM", "FMM"])
    p.add_argument("--nodes", nargs="+", required=True)
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", required=True, help="YYYY-MM-DD, exclusive")
    a = p.parse_args()

    caiso, failed = CAISO(), []
    for start, end in month_chunks(a.start, a.end):
        print(f"{a.market} {start.date()} -> {end.date()}")
        raw = fetch_chunk(caiso, a.market, start, end, a.nodes)
        if raw is None:
            failed.append((str(start.date()), str(end.date())))
            continue
        rows = to_lmp_rows(raw, a.market)
        n = load_chunk(
            rows, "gridstatus.CAISO.get_lmp",
            {"market": a.market, "nodes": a.nodes,
             "start": str(start.date()), "end": str(end.date())},
        )
        print(f"  loaded {n} new rows")

    if failed:
        print("FAILED chunks (rerun the same command to retry):", failed)


if __name__ == "__main__":
    main()