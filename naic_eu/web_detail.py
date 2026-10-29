"""HTML detailpagina voor fonds/aandeel met afdruk / PDF (browser print)."""

from __future__ import annotations

import html
from typing import Any


def _e(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return html.escape(f"{value:.2f}")
    return html.escape(str(value))


def _euro(value: float | None) -> str:
    if value is None:
        return "—"
    return html.escape(f"€ {value:.2f}")


def _pct(value: float | None) -> str:
    if value is None:
        return "—"
    return html.escape(f"{value:.2f}%")


def _large(value: float | None) -> str:
    if value is None:
        return "—"
    return html.escape(f"{value:,.0f}".replace(",", "."))


def _advice_label(advice: str | None) -> str:
    if advice == "K":
        return "Koop (K)"
    if advice == "v":
        return "Vermijden (v)"
    if advice == "n":
        return "Neutraal (n)"
    return advice or "—"


def render_fonds_detail_page(
    *,
    instrument: dict[str, Any],
    score: dict[str, Any] | None,
    fundamentals: list[dict[str, Any]],
    prices: list[dict[str, Any]],
    generated_at: str,
) -> str:
    ticker = instrument.get("ticker") or "?"
    name = instrument.get("name") or ticker
    title = f"{ticker} — {name}"

    price_rows = ""
    if prices:
        last = prices[0]
        oldest = prices[-1]
        lows = [p.get("low") or p.get("close") for p in prices if (p.get("low") or p.get("close")) is not None]
        highs = [p.get("high") or p.get("close") for p in prices if (p.get("high") or p.get("close")) is not None]
        price_rows = f"""
        <tr><th>Laatste koers ({_e(last.get('trade_date'))})</th><td>{_euro(last.get('close'))}</td></tr>
        <tr><th>Laagste (periode)</th><td>{_euro(min(lows) if lows else None)}</td></tr>
        <tr><th>Hoogste (periode)</th><td>{_euro(max(highs) if highs else None)}</td></tr>
        <tr><th>Datapunten koers</th><td>{len(prices)}</td></tr>
        <tr><th>Oudste datum</th><td>{_e(oldest.get('trade_date'))}</td></tr>
        """

    score_rows = ""
    if score:
        score_rows = f"""
        <tr><th>Advies</th><td><strong>{_e(_advice_label(score.get('advice')))}</strong></td></tr>
        <tr><th>Win/Loss ratio</th><td>{_e(score.get('win_loss_ratio'))}</td></tr>
        <tr><th>Koers</th><td>{_euro(score.get('current_price'))}</td></tr>
        <tr><th>Koopdrempel</th><td>{_euro(score.get('buy_threshold'))}</td></tr>
        <tr><th>Houd-drempel</th><td>{_euro(score.get('hold_threshold'))}</td></tr>
        <tr><th>Rendement 5j</th><td>{_pct(score.get('total_return_5y_pct'))}</td></tr>
        <tr><th>Omzet CAGR 10j</th><td>{_pct(score.get('revenue_cagr_10y'))}</td></tr>
        <tr><th>EPS CAGR 10j</th><td>{_pct(score.get('eps_cagr_10y'))}</td></tr>
        <tr><th>EV CAGR 10j</th><td>{_pct(score.get('equity_cagr_10y'))}</td></tr>
        <tr><th>Score datum</th><td>{_e(score.get('as_of_date'))}</td></tr>
        """

    fund_blocks = ""
    for f in fundamentals[:10]:
        fund_blocks += f"""
        <h3>Jaar {_e(f.get('fiscal_year'))}</h3>
        <table class="data">
          <tr><th>EPS</th><td>{_e(f.get('eps'))}</td></tr>
          <tr><th>Omzet</th><td>{_large(f.get('revenue'))}</td></tr>
          <tr><th>Nettowinst</th><td>{_large(f.get('net_income'))}</td></tr>
          <tr><th>Eigen vermogen per aandeel</th><td>{_e(f.get('equity_per_share'))}</td></tr>
        </table>
        """

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{ font-family: system-ui,Segoe UI,Roboto,sans-serif; color: #111; }}
    body {{ margin: 0; padding: 1rem 1.25rem 2rem; max-width: 900px; }}
    h1 {{ font-size: 1.5rem; margin: 0 0 0.25rem; }}
    .meta {{ color: #444; margin-bottom: 1rem; }}
    .toolbar {{ margin: 1rem 0 1.5rem; display: flex; gap: 0.75rem; flex-wrap: wrap; }}
    button {{
      font: inherit; padding: 0.5rem 1rem; cursor: pointer;
      border: 1px solid #333; border-radius: 6px; background: #f5f5f5;
    }}
    button.primary {{ background: #1a56db; color: #fff; border-color: #1a56db; }}
    section {{ margin-bottom: 1.5rem; }}
    h2 {{ font-size: 1.15rem; border-bottom: 1px solid #ccc; padding-bottom: 0.25rem; }}
    table.data {{ width: 100%; border-collapse: collapse; margin: 0.5rem 0 1rem; }}
    table.data th, table.data td {{ text-align: left; padding: 0.35rem 0.5rem; border-bottom: 1px solid #eee; }}
    table.data th {{ width: 42%; color: #333; font-weight: 600; }}
    .print-hint {{ font-size: 0.9rem; color: #555; }}
    @media print {{
      .no-print {{ display: none !important; }}
      body {{ padding: 0; max-width: none; }}
      a[href]:after {{ content: none; }}
    }}
  </style>
</head>
<body>
  <div class="no-print toolbar">
    <button type="button" class="primary" onclick="window.print()">Afdrukken / PDF</button>
    <button type="button" onclick="history.back()">Terug</button>
  </div>
  <p class="print-hint no-print">Kies in het afdrukvenster &quot;Opslaan als PDF&quot; om een PDF te maken.</p>

  <header>
    <h1>{html.escape(name)}</h1>
    <p class="meta">
      Ticker: <strong>{html.escape(ticker)}</strong>
      · Index: {_e(instrument.get('index_code'))}
      · Sector: {_e(instrument.get('sector'))}
      · ISIN: {_e(instrument.get('isin'))}
    </p>
    <p class="meta">Gegenereerd: {html.escape(generated_at)}</p>
  </header>

  <section>
    <h2>NAIC-analyse</h2>
    <table class="data">{score_rows or '<tr><td>Geen score beschikbaar</td></tr>'}</table>
  </section>

  <section>
    <h2>Koers</h2>
    <table class="data">{price_rows or '<tr><td>Geen koersdata</td></tr>'}</table>
  </section>

  <section>
    <h2>Fundamenten (jaarcijfers)</h2>
    {fund_blocks or '<p>Geen jaarcijfers</p>'}
  </section>

  <footer class="meta">
    <p>NAIC EU — fondsdetail · Alleen ter informatie, geen beleggingsadvies.</p>
  </footer>
</body>
</html>"""
