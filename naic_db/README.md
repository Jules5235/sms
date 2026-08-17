# NAIC EU Stocks Database — Proof of Concept

Proof-of-concept voor een EU-aandelendatabase met NAIC/SSG-achtige analyse, gericht op **AEX** en **BEL 20**.

## Datamodel

SQLite-database met de volgende tabellen:

| Tabel | Inhoud | Primaire bron |
|-------|--------|---------------|
| `instruments` | Master data (ticker, beurs, Yahoo/Stooq-symbolen) | `config/universes.yaml` |
| `index_membership` | Koppeling instrument ↔ AEX/BEL20 | Euronext (handmatig) |
| `price_daily` | Dagelijkse OHLCV-koersen (12 jaar) | Yahoo Finance → Stooq fallback |
| `fundamentals_annual` | Omzet, winst, EPS, eigen vermogen | Yahoo Finance |
| `dividends` | Ex-dividend data | Yahoo Finance |
| `naic_scores` | Berekende NAIC-kengetallen | Afgeleid |
| `ingest_log` | ETL-logboek | Intern |

Zie `schema.sql` voor het volledige schema inclusief de view `v_naic_ranking`.

## NAIC-berekeningen

Per instrument worden berekend:

- **H / L** — hoogste en laagste koers over 10 jaar
- **Koop-/houd-/verkoopzones** — H-L bereik in drie gelijke delen
- **Winst-verliesverhouding (wv)** — `(H - koers) / (koers - L)`
- **Advies** — `K` (koop) als koers in koopzone én wv ≥ 3; `v` (verkoop) in verkoopzone; anders `n`
- **CAGR** — omzet, EPS en eigen vermogen per aandeel over beschikbare jaren

## Installatie

```bash
cd naic_db
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Gebruik

```bash
# Volledige ETL (alle ~45 instrumenten, duurt enkele minuten)
python run_etl.py

# Snelle test met 5 instrumenten
python run_etl.py --limit 5

# Ranking bekijken
python query_ranking.py
python query_ranking.py --index AEX
python query_ranking.py --index BEL20
```

Database wordt opgeslagen in `data/naic_eu.db`.

## Databronnen per veld

| Veld | Bron | Opmerking |
|------|------|-----------|
| `price_daily.*` | Yahoo Finance (`yfinance`) | Fallback: Stooq CSV |
| `fundamentals_annual.revenue` | Yahoo `income_stmt` | Alleen december-jaar |
| `fundamentals_annual.net_income` | Yahoo `income_stmt` | |
| `fundamentals_annual.eps` | Berekend: net_income / shares | |
| `fundamentals_annual.equity_per_share` | Yahoo `balance_sheet` | Berekend |
| `dividends.amount` | Yahoo `ticker.dividends` | |
| `instruments.*` | Handmatig in `universes.yaml` | Periodiek bijwerken |

## Beperkingen

- Yahoo-data is **niet officieel** en kan gaten of fouten bevatten
- Fundamenten gaan zelden verder terug dan ~4–10 jaar via Yahoo
- ESEF/XBRL (officiële EU-jaarrekeningen) is **niet** geïntegreerd in deze PoC
- Niet geschikt voor commercieel gebruik zonder betaalde datalicentie
- NAIC-berekeningen zijn een **vereenvoudigde** versie van de volledige SSG/CoSA-methode

## Volgende stappen

1. ESEF/XBRL-parser toevoegen voor officiële fundamenten (vanaf 2020)
2. PostgreSQL-migratie voor productie
3. Automatische universe-update via Euronext index composition
4. Volledige CoSA-velden: TRg, PARg, schuldgraad, dividendgroei
5. Scheduled ETL (cron) voor wekelijkse koersupdates
