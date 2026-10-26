from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Result:
    op: str                      # "summary_stats"
    params: dict                 # exactly what was asked for
    source: dict                 # which table/market/node the numbers came from
    interval: tuple[datetime, datetime]
    values: dict[str, Any]       # the computed numbers
    method: str                  # plain-English description of the calculation
    sql: str                     # the exact query that ran
    rows_used: list[dict] = field(default_factory=list)