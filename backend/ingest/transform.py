import pandas as pd


def to_lmp_rows(raw: pd.DataFrame, label: str) -> pd.DataFrame:
    """Reshape a raw gridstatus LMP frame to match the lmp table."""
    start = pd.to_datetime(raw["Interval Start"])
    if start.dt.tz is None:
        raise ValueError("Interval Start has no timezone; refusing to guess")

    df = pd.DataFrame({
        "ts_utc": start.dt.tz_convert("UTC"),
        "market": label,
        "node_id": raw["Location"],
        "node_type": raw["Location Type"],
        "lmp": raw["LMP"],
        "energy": raw["Energy"],
        "congestion": raw["Congestion"],
        "loss": raw["Loss"],
        "ghg": raw["GHG"] if "GHG" in raw.columns else None,
    })
    return (df.drop_duplicates(["node_id", "market", "ts_utc"])
              .sort_values(["node_id", "ts_utc"]))