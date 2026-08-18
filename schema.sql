-- NAIC EU Stocks Database — SQLite schema
-- PoC voor AEX + BEL 20 met gratis databronnen (Yahoo Finance, Stooq)

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- instruments: master data per beursgenoteerd instrument
-- Bronnen: handmatig (universe YAML) + Yahoo Finance (metadata)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS instruments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT    NOT NULL,           -- interne code (bijv. ASML)
    exchange        TEXT    NOT NULL,           -- AMS, BRU, PAR, ...
    isin            TEXT,
    name            TEXT,
    currency        TEXT    DEFAULT 'EUR',
    yahoo_symbol    TEXT,                       -- bijv. ASML.AS
    stooq_symbol    TEXT,                       -- bijv. asml.nl
    sector          TEXT,
    country         TEXT,
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT    DEFAULT (datetime('now')),
    updated_at      TEXT    DEFAULT (datetime('now')),
    UNIQUE (ticker, exchange)
);

-- ---------------------------------------------------------------------------
-- index_membership: koppeling instrument ↔ index
-- Bron: Euronext index composition (handmatig in universes.yaml)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS index_membership (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id   INTEGER NOT NULL REFERENCES instruments(id),
    index_code      TEXT    NOT NULL,           -- AEX, BEL20
    weight_pct      REAL,                       -- indexgewicht (%)
    effective_from  TEXT,
    effective_to    TEXT,
    UNIQUE (instrument_id, index_code, effective_from)
);

-- ---------------------------------------------------------------------------
-- price_daily: dagelijkse koersen (EOD)
-- Bron: Yahoo Finance (primair), Stooq (fallback)
-- Velden: open, high, low, close, volume, adj_close
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS price_daily (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id   INTEGER NOT NULL REFERENCES instruments(id),
    trade_date      TEXT    NOT NULL,           -- YYYY-MM-DD
    open            REAL,
    high            REAL,
    low             REAL,
    close           REAL,
    adj_close       REAL,
    volume          REAL,
    source          TEXT    NOT NULL,           -- yahoo, stooq
    ingested_at     TEXT    DEFAULT (datetime('now')),
    UNIQUE (instrument_id, trade_date, source)
);

CREATE INDEX IF NOT EXISTS idx_price_daily_instrument_date
    ON price_daily (instrument_id, trade_date);

-- ---------------------------------------------------------------------------
-- fundamentals_annual: jaarlijkse fundamentele cijfers
-- Bron: Yahoo Finance (primair)
-- NAIC gebruikt: revenue, net_income, eps, equity_per_share (10 jaar)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fundamentals_annual (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id       INTEGER NOT NULL REFERENCES instruments(id),
    fiscal_year         INTEGER NOT NULL,
    period_end          TEXT,                   -- YYYY-MM-DD
    revenue             REAL,                   -- omzet
    gross_profit        REAL,
    operating_income    REAL,
    net_income          REAL,                   -- nettowinst
    eps                 REAL,                   -- winst per aandeel
    shares_outstanding  REAL,
    total_equity        REAL,                   -- eigen vermogen
    equity_per_share    REAL,                   -- EVpA (berekend)
    total_debt          REAL,
    free_cash_flow      REAL,
    currency            TEXT    DEFAULT 'EUR',
    source              TEXT    NOT NULL,
    ingested_at         TEXT    DEFAULT (datetime('now')),
    UNIQUE (instrument_id, fiscal_year, source)
);

-- ---------------------------------------------------------------------------
-- dividends: dividenduitkeringen
-- Bron: Yahoo Finance
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dividends (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id   INTEGER NOT NULL REFERENCES instruments(id),
    ex_date         TEXT    NOT NULL,           -- ex-dividend datum
    amount          REAL    NOT NULL,
    currency        TEXT    DEFAULT 'EUR',
    source          TEXT    NOT NULL,
    ingested_at     TEXT    DEFAULT (datetime('now')),
    UNIQUE (instrument_id, ex_date, source)
);

-- ---------------------------------------------------------------------------
-- naic_scores: berekende NAIC/SSG-kengetallen
-- Afgeleid van price_daily + fundamentals_annual
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS naic_scores (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id       INTEGER NOT NULL REFERENCES instruments(id),
    as_of_date          TEXT    NOT NULL,
    current_price       REAL,
    price_high_10y      REAL,                   -- H: hoogste koers in lookback
    price_low_10y       REAL,                   -- L: laagste koers in lookback
    buy_threshold       REAL,                   -- L + (H-L)/3
    hold_threshold      REAL,                   -- L + 2*(H-L)/3
    upside              REAL,                   -- H - current
    downside            REAL,                   -- current - L
    win_loss_ratio      REAL,                   -- wv = upside / downside
    advice              TEXT,                   -- K (koop), n (neutraal), v (verkoop)
    total_return_5y_pct REAL,                   -- geschat 5-jaars totaalrendement
    revenue_cagr_10y    REAL,
    eps_cagr_10y        REAL,
    equity_cagr_10y     REAL,
    computed_at         TEXT    DEFAULT (datetime('now')),
    UNIQUE (instrument_id, as_of_date)
);

-- ---------------------------------------------------------------------------
-- ingest_log: ETL-tracering
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingest_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name        TEXT    NOT NULL,
    instrument_id   INTEGER REFERENCES instruments(id),
    status          TEXT    NOT NULL,           -- ok, error, skipped
    records_count   INTEGER DEFAULT 0,
    message         TEXT,
    started_at      TEXT    DEFAULT (datetime('now')),
    finished_at     TEXT
);

-- Handige view: laatste NAIC-scores per index
CREATE VIEW IF NOT EXISTS v_naic_ranking AS
SELECT
    i.ticker,
    i.name,
    i.exchange,
    im.index_code,
    n.as_of_date,
    n.current_price,
    n.win_loss_ratio,
    n.advice,
    n.total_return_5y_pct,
    n.revenue_cagr_10y,
    n.eps_cagr_10y,
    n.buy_threshold,
    n.hold_threshold
FROM naic_scores n
JOIN instruments i ON i.id = n.instrument_id
JOIN index_membership im ON im.instrument_id = i.id
WHERE im.effective_to IS NULL
  AND n.as_of_date = (
      SELECT MAX(n2.as_of_date) FROM naic_scores n2
      WHERE n2.instrument_id = n.instrument_id
  )
ORDER BY im.index_code,
    CASE n.advice WHEN 'K' THEN 0 WHEN 'n' THEN 1 ELSE 2 END,
    n.win_loss_ratio DESC;
