"""Optional Stooq fallback for EOD prices (CSV endpoint)."""

from __future__ import annotations

from datetime import date, timedelta
from io import StringIO

import pandas as pd
import requests

STOOQ_URL = "https://stooq.com/q/d/l/"


def fetch_prices(stooq_symbol: str, years: int = 12) -> pd.DataFrame:
    end = date.today()
    start = end - timedelta(days=years * 365)
    params = {
        "s": stooq_symbol.lower(),
        "d1": start.strftime("%Y%m%d"),
        "d2": end.strftime("%Y%m%d"),
        "i": "d",
    }
    resp = requests.get(STOOQ_URL, params=params, timeout=30)
    resp.raise_for_status()
    if "Exceeded the daily hits limit" in resp.text:
        raise RuntimeError("Stooq daglimiet bereikt")

    df = pd.read_csv(StringIO(resp.text))
    if df.empty or "Date" not in df.columns:
        return pd.DataFrame()

    df["trade_date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    df["adj_close"] = df["close"]
    return df[["trade_date", "open", "high", "low", "close", "adj_close", "volume"]]
