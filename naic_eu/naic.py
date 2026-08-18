"""NAIC / SSG-achtige berekeningen op basis van opgeslagen data."""

from __future__ import annotations

import math
import sqlite3
from datetime import date, timedelta


LOOKBACK_YEARS = 10
WV_BUY_THRESHOLD = 3.0


def compute_cagr(start: float | None, end: float | None, years: int) -> float | None:
    if start is None or end is None or start <= 0 or end <= 0 or years <= 0:
        return None
    return (end / start) ** (1 / years) - 1


def compute_naic_for_instrument(
    conn: sqlite3.Connection,
    instrument_id: int,
    as_of_date: str | None = None,
) -> dict | None:
    as_of = as_of_date or date.today().isoformat()
    cutoff = (date.fromisoformat(as_of) - timedelta(days=LOOKBACK_YEARS * 365)).isoformat()

    price_row = conn.execute(
        """
        SELECT close, high, low, trade_date
        FROM price_daily
        WHERE instrument_id = ? AND trade_date <= ?
        ORDER BY trade_date DESC
        LIMIT 1
        """,
        (instrument_id, as_of),
    ).fetchone()
    if not price_row:
        return None

    current_price = price_row["close"]
    hist = conn.execute(
        """
        SELECT MAX(high) AS price_high, MIN(low) AS price_low
        FROM price_daily
        WHERE instrument_id = ? AND trade_date >= ? AND trade_date <= ?
        """,
        (instrument_id, cutoff, as_of),
    ).fetchone()

    price_high = hist["price_high"]
    price_low = hist["price_low"]
    if not price_high or not price_low or current_price is None:
        return None

    span = price_high - price_low
    buy_threshold = price_low + span / 3
    hold_threshold = price_low + 2 * span / 3
    upside = price_high - current_price
    downside = current_price - price_low

    if downside <= 0:
        win_loss_ratio = None
    else:
        win_loss_ratio = upside / downside

    if current_price <= buy_threshold and win_loss_ratio is not None and win_loss_ratio >= WV_BUY_THRESHOLD:
        advice = "K"
    elif current_price >= hold_threshold:
        advice = "v"
    else:
        advice = "n"

    fund_rows = conn.execute(
        """
        SELECT fiscal_year, revenue, eps, equity_per_share
        FROM fundamentals_annual
        WHERE instrument_id = ?
        ORDER BY fiscal_year
        """,
        (instrument_id,),
    ).fetchall()

    revenue_cagr = eps_cagr = equity_cagr = None
    total_return_5y = None

    if len(fund_rows) >= 2:
        first, last = fund_rows[0], fund_rows[-1]
        years = last["fiscal_year"] - first["fiscal_year"]
        if years > 0:
            revenue_cagr = compute_cagr(first["revenue"], last["revenue"], years)
            eps_cagr = compute_cagr(first["eps"], last["eps"], years)
            equity_cagr = compute_cagr(first["equity_per_share"], last["equity_per_share"], years)

    if eps_cagr is not None:
        total_return_5y = ((1 + eps_cagr) ** 5 - 1) * 100

    return {
        "instrument_id": instrument_id,
        "as_of_date": as_of,
        "current_price": current_price,
        "price_high_10y": price_high,
        "price_low_10y": price_low,
        "buy_threshold": buy_threshold,
        "hold_threshold": hold_threshold,
        "upside": upside,
        "downside": downside,
        "win_loss_ratio": win_loss_ratio,
        "advice": advice,
        "total_return_5y_pct": total_return_5y,
        "revenue_cagr_10y": revenue_cagr,
        "eps_cagr_10y": eps_cagr,
        "equity_cagr_10y": equity_cagr,
    }


def save_naic_score(conn: sqlite3.Connection, score: dict) -> None:
    conn.execute(
        """
        INSERT INTO naic_scores (
            instrument_id, as_of_date, current_price, price_high_10y, price_low_10y,
            buy_threshold, hold_threshold, upside, downside, win_loss_ratio,
            advice, total_return_5y_pct, revenue_cagr_10y, eps_cagr_10y, equity_cagr_10y
        ) VALUES (
            :instrument_id, :as_of_date, :current_price, :price_high_10y, :price_low_10y,
            :buy_threshold, :hold_threshold, :upside, :downside, :win_loss_ratio,
            :advice, :total_return_5y_pct, :revenue_cagr_10y, :eps_cagr_10y, :equity_cagr_10y
        )
        ON CONFLICT(instrument_id, as_of_date) DO UPDATE SET
            current_price = excluded.current_price,
            price_high_10y = excluded.price_high_10y,
            price_low_10y = excluded.price_low_10y,
            buy_threshold = excluded.buy_threshold,
            hold_threshold = excluded.hold_threshold,
            upside = excluded.upside,
            downside = excluded.downside,
            win_loss_ratio = excluded.win_loss_ratio,
            advice = excluded.advice,
            total_return_5y_pct = excluded.total_return_5y_pct,
            revenue_cagr_10y = excluded.revenue_cagr_10y,
            eps_cagr_10y = excluded.eps_cagr_10y,
            equity_cagr_10y = excluded.equity_cagr_10y,
            computed_at = datetime('now')
        """,
        score,
    )
    conn.commit()


def recompute_all(conn: sqlite3.Connection, as_of_date: str | None = None) -> int:
    ids = [row["id"] for row in conn.execute("SELECT id FROM instruments WHERE is_active = 1")]
    count = 0
    for instrument_id in ids:
        score = compute_naic_for_instrument(conn, instrument_id, as_of_date)
        if score and score["win_loss_ratio"] is not None and not math.isnan(score["win_loss_ratio"]):
            save_naic_score(conn, score)
            count += 1
    return count
