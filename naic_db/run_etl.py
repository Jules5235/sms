#!/usr/bin/env python3
"""ETL-pipeline: laad AEX + BEL 20 data en bereken NAIC-scores."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

# Zorg dat het pakket importeerbaar is vanuit de projectmap
sys.path.insert(0, str(Path(__file__).resolve().parent))

from naic_db.db import connect, init_db, log_ingest
from naic_db.fetch_stooq import fetch_prices as fetch_stooq_prices
from naic_db.fetch_yahoo import (
    fetch_dividends,
    fetch_fundamentals_annual,
    fetch_prices as fetch_yahoo_prices,
)
from naic_db.naic import recompute_all
from naic_db.universe import InstrumentDef, load_universe


def upsert_instrument(conn: sqlite3.Connection, inst: InstrumentDef) -> int:
    conn.execute(
        """
        INSERT INTO instruments (ticker, exchange, name, yahoo_symbol, stooq_symbol, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(ticker, exchange) DO UPDATE SET
            name = excluded.name,
            yahoo_symbol = excluded.yahoo_symbol,
            stooq_symbol = excluded.stooq_symbol,
            updated_at = datetime('now')
        """,
        (inst.ticker, inst.exchange, inst.name, inst.yahoo_symbol, inst.stooq_symbol),
    )
    row = conn.execute(
        "SELECT id FROM instruments WHERE ticker = ? AND exchange = ?",
        (inst.ticker, inst.exchange),
    ).fetchone()
    instrument_id = row["id"]

    conn.execute(
        """
        INSERT INTO index_membership (instrument_id, index_code, weight_pct, effective_from)
        VALUES (?, ?, ?, date('now'))
        ON CONFLICT(instrument_id, index_code, effective_from) DO UPDATE SET
            weight_pct = excluded.weight_pct
        """,
        (instrument_id, inst.index_code, inst.weight_pct),
    )
    conn.commit()
    return instrument_id


def load_prices(conn: sqlite3.Connection, instrument_id: int, inst: InstrumentDef) -> int:
    source = "yahoo"
    try:
        df = fetch_yahoo_prices(inst.yahoo_symbol)
    except Exception as exc:
        log_ingest(conn, "prices", "error", instrument_id, message=f"Yahoo: {exc}")
        df = None

    if df is None or df.empty:
        try:
            df = fetch_stooq_prices(inst.stooq_symbol)
            source = "stooq"
        except Exception as exc:
            log_ingest(conn, "prices", "error", instrument_id, message=f"Stooq: {exc}")
            return 0

    count = 0
    for _, row in df.iterrows():
        conn.execute(
            """
            INSERT INTO price_daily (
                instrument_id, trade_date, open, high, low, close, adj_close, volume, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(instrument_id, trade_date, source) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                adj_close = excluded.adj_close,
                volume = excluded.volume,
                ingested_at = datetime('now')
            """,
            (
                instrument_id,
                row["trade_date"],
                row.get("open"),
                row.get("high"),
                row.get("low"),
                row.get("close"),
                row.get("adj_close"),
                row.get("volume"),
                source,
            ),
        )
        count += 1
    conn.commit()
    log_ingest(conn, "prices", "ok", instrument_id, count, f"source={source}")
    return count


def load_fundamentals(conn: sqlite3.Connection, instrument_id: int, inst: InstrumentDef) -> int:
    try:
        df = fetch_fundamentals_annual(inst.yahoo_symbol)
    except Exception as exc:
        log_ingest(conn, "fundamentals", "error", instrument_id, message=str(exc))
        return 0

    if df.empty:
        log_ingest(conn, "fundamentals", "skipped", instrument_id, message="geen data")
        return 0

    count = 0
    for _, row in df.iterrows():
        conn.execute(
            """
            INSERT INTO fundamentals_annual (
                instrument_id, fiscal_year, period_end, revenue, gross_profit,
                operating_income, net_income, eps, shares_outstanding, total_equity,
                equity_per_share, total_debt, free_cash_flow, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'yahoo')
            ON CONFLICT(instrument_id, fiscal_year, source) DO UPDATE SET
                period_end = excluded.period_end,
                revenue = excluded.revenue,
                gross_profit = excluded.gross_profit,
                operating_income = excluded.operating_income,
                net_income = excluded.net_income,
                eps = excluded.eps,
                shares_outstanding = excluded.shares_outstanding,
                total_equity = excluded.total_equity,
                equity_per_share = excluded.equity_per_share,
                total_debt = excluded.total_debt,
                free_cash_flow = excluded.free_cash_flow,
                ingested_at = datetime('now')
            """,
            (
                instrument_id,
                int(row["fiscal_year"]),
                row.get("period_end"),
                row.get("revenue"),
                row.get("gross_profit"),
                row.get("operating_income"),
                row.get("net_income"),
                row.get("eps"),
                row.get("shares_outstanding"),
                row.get("total_equity"),
                row.get("equity_per_share"),
                row.get("total_debt"),
                row.get("free_cash_flow"),
            ),
        )
        count += 1
    conn.commit()
    log_ingest(conn, "fundamentals", "ok", instrument_id, count)
    return count


def load_dividends(conn: sqlite3.Connection, instrument_id: int, inst: InstrumentDef) -> int:
    try:
        df = fetch_dividends(inst.yahoo_symbol)
    except Exception as exc:
        log_ingest(conn, "dividends", "error", instrument_id, message=str(exc))
        return 0

    if df.empty:
        return 0

    count = 0
    for _, row in df.iterrows():
        conn.execute(
            """
            INSERT INTO dividends (instrument_id, ex_date, amount, source)
            VALUES (?, ?, ?, 'yahoo')
            ON CONFLICT(instrument_id, ex_date, source) DO UPDATE SET
                amount = excluded.amount,
                ingested_at = datetime('now')
            """,
            (instrument_id, row["ex_date"], row["amount"]),
        )
        count += 1
    conn.commit()
    log_ingest(conn, "dividends", "ok", instrument_id, count)
    return count


def run_etl(db_path: Path | None = None, limit: int | None = None) -> None:
    conn = connect(db_path)
    init_db(conn)

    universe = load_universe()
    if limit:
        universe = universe[:limit]

    print(f"Laden van {len(universe)} instrumenten...")
    stats = {"prices": 0, "fundamentals": 0, "dividends": 0}

    for i, inst in enumerate(universe, 1):
        print(f"[{i}/{len(universe)}] {inst.ticker} ({inst.index_code})...", end=" ", flush=True)
        instrument_id = upsert_instrument(conn, inst)
        p = load_prices(conn, instrument_id, inst)
        f = load_fundamentals(conn, instrument_id, inst)
        d = load_dividends(conn, instrument_id, inst)
        stats["prices"] += p
        stats["fundamentals"] += f
        stats["dividends"] += d
        print(f"koersen={p}, fund={f}, div={d}")

    scored = recompute_all(conn)
    print(f"\nKlaar. Koersrecords: {stats['prices']}, fundamenten: {stats['fundamentals']}, "
          f"dividenden: {stats['dividends']}, NAIC-scores: {scored}")


def main() -> None:
    parser = argparse.ArgumentParser(description="NAIC EU database ETL")
    parser.add_argument("--db", type=Path, help="Pad naar SQLite database")
    parser.add_argument("--limit", type=int, help="Beperk aantal instrumenten (voor tests)")
    args = parser.parse_args()
    run_etl(args.db, args.limit)


if __name__ == "__main__":
    main()
