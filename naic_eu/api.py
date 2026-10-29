"""REST API voor NAIC-database (read-only)."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Generator

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from naic_eu.paths import DEFAULT_DB_PATH
from naic_eu.web_detail import render_fonds_detail_page

API_HOST = os.environ.get("NAIC_API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("NAIC_API_PORT", "8080"))


app = FastAPI(
    title="NAIC EU API",
    description="Read-only REST API voor AEX + BEL 20 NAIC-database",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("NAIC_CORS_ORIGINS", "*").split(","),
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_db() -> Generator[sqlite3.Connection, None, None]:
    if not DEFAULT_DB_PATH.exists():
        raise HTTPException(status_code=503, detail=f"Database niet gevonden: {DEFAULT_DB_PATH}")
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def fetch_all(conn: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict[str, Any]]:
    return rows_to_dicts(conn.execute(query, params).fetchall())


def fetch_one(conn: sqlite3.Connection, query: str, params: tuple = ()) -> dict[str, Any] | None:
    row = conn.execute(query, params).fetchone()
    return dict(row) if row else None


@app.get("/health")
def health() -> dict[str, Any]:
    exists = DEFAULT_DB_PATH.exists()
    result: dict[str, Any] = {
        "status": "ok" if exists else "degraded",
        "database": str(DEFAULT_DB_PATH),
    }
    if exists:
        conn = sqlite3.connect(DEFAULT_DB_PATH)
        try:
            result["instruments"] = conn.execute("SELECT COUNT(*) FROM instruments").fetchone()[0]
            result["naic_scores"] = conn.execute("SELECT COUNT(*) FROM naic_scores").fetchone()[0]
            result["latest_score_date"] = conn.execute("SELECT MAX(as_of_date) FROM naic_scores").fetchone()[0]
        finally:
            conn.close()
    return result


@app.get("/api/stats")
def stats(conn: sqlite3.Connection = Depends(get_db)) -> dict[str, int]:
    tables = ["instruments", "price_daily", "fundamentals_annual", "dividends", "naic_scores"]
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}


@app.get("/api/ranking")
def ranking(
    index: str | None = Query(None, description="Filter op AEX of BEL20"),
    advice: str | None = Query(None, description="Filter op K, n of v"),
    conn: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    query = "SELECT * FROM v_naic_ranking WHERE 1=1"
    params: list[Any] = []
    if index:
        query += " AND index_code = ?"
        params.append(index.upper())
    if advice:
        query += " AND advice = ?"
        params.append(advice)
    query += (
        " ORDER BY index_code, CASE advice WHEN 'K' THEN 0 WHEN 'n' THEN 1 ELSE 2 END,"
        " win_loss_ratio DESC"
    )
    return fetch_all(conn, query, tuple(params))


@app.get("/api/ranking/{index_code}")
def ranking_by_index(index_code: str, conn: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
    code = index_code.upper()
    if code not in ("AEX", "BEL20"):
        raise HTTPException(status_code=400, detail="index_code moet AEX of BEL20 zijn")
    return fetch_all(
        conn,
        """
        SELECT * FROM v_naic_ranking WHERE index_code = ?
        ORDER BY CASE advice WHEN 'K' THEN 0 WHEN 'n' THEN 1 ELSE 2 END, win_loss_ratio DESC
        """,
        (code,),
    )


@app.get("/api/instruments")
def instruments(
    index: str | None = Query(None),
    conn: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    if index:
        return fetch_all(
            conn,
            """
            SELECT i.*, im.index_code, im.weight_pct
            FROM instruments i
            JOIN index_membership im ON im.instrument_id = i.id
            WHERE im.index_code = ? AND im.effective_to IS NULL
            ORDER BY i.ticker
            """,
            (index.upper(),),
        )
    return fetch_all(conn, "SELECT * FROM instruments WHERE is_active = 1 ORDER BY ticker")


@app.get("/api/instruments/{ticker}")
def instrument_detail(ticker: str, conn: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    payload = _fonds_detail_payload(ticker, conn)
    return {
        "instrument": payload["instrument"],
        "naic_score": payload["naic_score"],
        "fundamentals": payload["fundamentals"],
    }


def _fonds_detail_payload(ticker: str, conn: sqlite3.Connection) -> dict[str, Any]:
    upper = ticker.upper()
    inst = fetch_one(
        conn,
        """
        SELECT i.*, im.index_code, im.weight_pct
        FROM instruments i
        LEFT JOIN index_membership im ON im.instrument_id = i.id AND im.effective_to IS NULL
        WHERE i.ticker = ?
        LIMIT 1
        """,
        (upper,),
    )
    if not inst:
        raise HTTPException(status_code=404, detail=f"Instrument {ticker} niet gevonden")

    score = fetch_one(
        conn,
        """
        SELECT * FROM naic_scores
        WHERE instrument_id = (SELECT id FROM instruments WHERE ticker = ? LIMIT 1)
        ORDER BY as_of_date DESC LIMIT 1
        """,
        (upper,),
    )
    fundamentals = fetch_all(
        conn,
        """
        SELECT fiscal_year, revenue, net_income, eps, equity_per_share
        FROM fundamentals_annual
        WHERE instrument_id = (SELECT id FROM instruments WHERE ticker = ? LIMIT 1)
        ORDER BY fiscal_year DESC LIMIT 10
        """,
        (upper,),
    )
    prices = fetch_all(
        conn,
        """
        SELECT trade_date, open, high, low, close, adj_close, volume
        FROM price_daily
        WHERE instrument_id = (SELECT id FROM instruments WHERE ticker = ? LIMIT 1)
        ORDER BY trade_date DESC LIMIT 365
        """,
        (upper,),
    )
    return {
        "instrument": inst,
        "naic_score": score,
        "fundamentals": fundamentals,
        "prices": prices,
    }


@app.get("/fonds/{ticker}", response_class=HTMLResponse)
def fonds_detail_page(ticker: str, conn: sqlite3.Connection = Depends(get_db)) -> HTMLResponse:
    """Fondsdetailpagina met afdrukken / opslaan als PDF (browser)."""
    payload = _fonds_detail_payload(ticker, conn)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = render_fonds_detail_page(
        instrument=payload["instrument"],
        score=payload["naic_score"],
        fundamentals=payload["fundamentals"],
        prices=payload["prices"],
        generated_at=generated,
    )
    return HTMLResponse(content=html)


@app.get("/api/instruments/{ticker}/prices")
def instrument_prices(
    ticker: str,
    limit: int = Query(365, ge=1, le=5000),
    conn: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = fetch_all(
        conn,
        """
        SELECT trade_date, open, high, low, close, adj_close, volume
        FROM price_daily
        WHERE instrument_id = (SELECT id FROM instruments WHERE ticker = ? LIMIT 1)
        ORDER BY trade_date DESC LIMIT ?
        """,
        (ticker.upper(), limit),
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"Geen koersdata voor {ticker}")
    return rows


def main() -> None:
    import uvicorn

    uvicorn.run(
        "naic_eu.api:app",
        host=API_HOST,
        port=API_PORT,
        reload=os.environ.get("NAIC_API_RELOAD", "") == "1",
    )
