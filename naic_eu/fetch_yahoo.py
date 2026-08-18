"""Fetch market data from Yahoo Finance via yfinance."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import yfinance as yf

LOOKBACK_YEARS = 12


def fetch_prices(yahoo_symbol: str, years: int = LOOKBACK_YEARS) -> pd.DataFrame:
    start = date.today() - timedelta(days=years * 365)
    ticker = yf.Ticker(yahoo_symbol)
    df = ticker.history(start=start.isoformat(), auto_adjust=False)
    if df.empty:
        return df

    df = df.reset_index()
    df["trade_date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )
    return df[["trade_date", "open", "high", "low", "close", "adj_close", "volume"]]


def fetch_dividends(yahoo_symbol: str) -> pd.DataFrame:
    ticker = yf.Ticker(yahoo_symbol)
    series = ticker.dividends
    if series is None or series.empty:
        return pd.DataFrame(columns=["ex_date", "amount"])

    df = series.reset_index()
    df.columns = ["ex_date", "amount"]
    df["ex_date"] = pd.to_datetime(df["ex_date"]).dt.strftime("%Y-%m-%d")
    return df


def fetch_fundamentals_annual(yahoo_symbol: str) -> pd.DataFrame:
    """Extract annual fundamentals from Yahoo income/balance/cashflow statements."""
    ticker = yf.Ticker(yahoo_symbol)
    income = ticker.income_stmt
    balance = ticker.balance_sheet
    cashflow = ticker.cashflow

    if income is None or income.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    for col in income.columns:
        period_end = pd.Timestamp(col)
        if period_end.month != 12:
            continue

        fiscal_year = period_end.year
        revenue = _pick(income, col, ["Total Revenue", "Operating Revenue"])
        net_income = _pick(income, col, ["Net Income", "Net Income Common Stockholders"])
        gross_profit = _pick(income, col, ["Gross Profit"])
        operating_income = _pick(income, col, ["Operating Income", "EBIT"])

        total_equity = _pick(balance, col, ["Stockholders Equity", "Total Equity Gross Minority Interest"])
        total_debt = _pick(balance, col, ["Total Debt", "Long Term Debt"])
        shares = _pick(balance, col, ["Ordinary Shares Number", "Share Issued", "Common Stock"])
        fcf = _pick(cashflow, col, ["Free Cash Flow"])

        eps = None
        if net_income is not None and shares and shares != 0:
            eps = net_income / shares

        equity_per_share = None
        if total_equity is not None and shares and shares != 0:
            equity_per_share = total_equity / shares

        rows.append(
            {
                "fiscal_year": fiscal_year,
                "period_end": period_end.strftime("%Y-%m-%d"),
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "eps": eps,
                "shares_outstanding": shares,
                "total_equity": total_equity,
                "equity_per_share": equity_per_share,
                "total_debt": total_debt,
                "free_cash_flow": fcf,
            }
        )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values("fiscal_year")
    return df.drop_duplicates(subset=["fiscal_year"], keep="last")


def _pick(df: pd.DataFrame | None, col, keys: list[str]) -> float | None:
    if df is None or df.empty or col not in df.columns:
        return None
    for key in keys:
        if key in df.index:
            val = df.loc[key, col]
            if pd.notna(val):
                return float(val)
    return None
