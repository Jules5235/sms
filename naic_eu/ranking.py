"""Toon NAIC-ranking per index uit de database."""

from __future__ import annotations

import argparse
from pathlib import Path

from naic_eu.db import connect


def show_ranking(db_path: Path | str | None = None, index_code: str | None = None) -> None:
    conn = connect(db_path)
    query = "SELECT * FROM v_naic_ranking"
    params: tuple = ()
    if index_code:
        query += " WHERE index_code = ?"
        params = (index_code.upper(),)
    query += (
        " ORDER BY index_code, CASE advice WHEN 'K' THEN 0 WHEN 'n' THEN 1 ELSE 2 END,"
        " win_loss_ratio DESC"
    )

    rows = conn.execute(query, params).fetchall()
    if not rows:
        print("Geen NAIC-scores gevonden. Draai eerst: naic-etl")
        return

    current_index = None
    for row in rows:
        if row["index_code"] != current_index:
            current_index = row["index_code"]
            print(f"\n=== {current_index} ===")
            print(f"{'Ticker':<8} {'Naam':<28} {'Koers':>8} {'wv':>6} {'Advies':>6} {'EPS CAGR':>9}")
            print("-" * 72)

        wv = f"{row['win_loss_ratio']:.2f}" if row["win_loss_ratio"] is not None else "  n/a"
        eps = f"{row['eps_cagr_10y']*100:.1f}%" if row["eps_cagr_10y"] is not None else "    n/a"
        price = f"{row['current_price']:.2f}" if row["current_price"] is not None else "   n/a"
        name = (row["name"] or "")[:28]
        print(f"{row['ticker']:<8} {name:<28} {price:>8} {wv:>6} {row['advice']:>6} {eps:>9}")


def main() -> None:
    parser = argparse.ArgumentParser(description="NAIC ranking viewer")
    parser.add_argument("--db", type=Path)
    parser.add_argument("--index", choices=["AEX", "BEL20"], help="Filter op index")
    args = parser.parse_args()
    show_ranking(args.db, args.index)


if __name__ == "__main__":
    main()
