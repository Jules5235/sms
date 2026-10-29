package nl.jules.naic.ui.detail

import android.content.Context
import android.print.PrintAttributes
import android.print.PrintManager
import android.webkit.WebView
import android.webkit.WebViewClient
import nl.jules.naic.remote.model.Fundamental
import nl.jules.naic.remote.model.Instrument
import nl.jules.naic.remote.model.NaicScore
import nl.jules.naic.remote.model.PricePoint
import nl.jules.naic.ui.theme.adviceLabel
import java.util.Locale

fun printFondsDetail(
    context: Context,
    instrument: Instrument,
    score: NaicScore?,
    fundamentals: List<Fundamental>,
    prices: List<PricePoint>,
) {
    val html = buildDetailPrintHtml(instrument, score, fundamentals, prices)
    val jobName = "NAIC-${instrument.ticker}"
    val webView = WebView(context)
    webView.webViewClient = object : WebViewClient() {
        override fun onPageFinished(view: WebView?, url: String?) {
            val printManager = context.getSystemService(Context.PRINT_SERVICE) as PrintManager
            val adapter = view?.createPrintDocumentAdapter(jobName) ?: return
            printManager.print(
                jobName,
                adapter,
                PrintAttributes.Builder().build(),
            )
        }
    }
    webView.loadDataWithBaseURL(null, html, "text/HTML", "UTF-8", null)
}

private fun buildDetailPrintHtml(
    instrument: Instrument,
    score: NaicScore?,
    fundamentals: List<Fundamental>,
    prices: List<PricePoint>,
): String {
    val name = escape(instrument.name ?: instrument.ticker)
    val ticker = escape(instrument.ticker)
    val index = escape(instrument.indexCode ?: "—")
    val sector = escape(instrument.sector ?: "—")

    val scoreBlock = buildString {
        if (score == null) {
            append("<p>Geen NAIC-score beschikbaar</p>")
        } else {
            append("<table>")
            score.advice?.let { append(row("Advies", escape(adviceLabel(it)))) }
            score.winLossRatio?.let { append(row("Win/Loss ratio", fmt(it))) }
            score.currentPrice?.let { append(row("Koers", "€ ${fmt(it)}")) }
            score.buyThreshold?.let { append(row("Koopdrempel", "€ ${fmt(it)}")) }
            score.holdThreshold?.let { append(row("Houd-drempel", "€ ${fmt(it)}")) }
            score.totalReturn5yPct?.let { append(row("Rendement 5j", "${fmt(it)}%")) }
            score.revenueCagr10y?.let { append(row("Omzet CAGR 10j", "${fmt(it)}%")) }
            score.epsCagr10y?.let { append(row("EPS CAGR 10j", "${fmt(it)}%")) }
            score.equityCagr10y?.let { append(row("EV CAGR 10j", "${fmt(it)}%")) }
            append("</table>")
        }
    }

    val priceBlock = if (prices.isEmpty()) {
        "<p>Geen koersdata</p>"
    } else {
        val last = prices.first()
        val lows = prices.mapNotNull { it.low ?: it.close }
        val highs = prices.mapNotNull { it.high ?: it.close }
        buildString {
            append("<table>")
            val closeText = last.close?.let { "€ ${fmt(it)}" } ?: "—"
            append(row("Laatste koers (${escape(last.tradeDate ?: "—")})", closeText))
            if (lows.isNotEmpty()) append(row("Laagste (periode)", "€ ${fmt(lows.min())}"))
            if (highs.isNotEmpty()) append(row("Hoogste (periode)", "€ ${fmt(highs.max())}"))
            append(row("Datapunten", prices.size.toString()))
            append("</table>")
        }
    }

    val fundBlock = buildString {
        if (fundamentals.isEmpty()) {
            append("<p>Geen jaarcijfers</p>")
        } else {
            fundamentals.take(10).forEach { f ->
                append("<h3>Jaar ${escape(f.fiscalYear?.toString() ?: "—")}</h3><table>")
                f.eps?.let { append(row("EPS", fmt(it))) }
                f.revenue?.let { append(row("Omzet", fmtLarge(it))) }
                f.netIncome?.let { append(row("Nettowinst", fmtLarge(it))) }
                append("</table>")
            }
        }
    }

    return """
        <!DOCTYPE html><html lang="nl"><head><meta charset="utf-8"/>
        <style>
          body { font-family: sans-serif; padding: 12px; color: #111; }
          h1 { font-size: 20px; margin: 0 0 8px; }
          h2 { font-size: 16px; border-bottom: 1px solid #ccc; }
          h3 { font-size: 14px; margin-top: 12px; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
          th, td { text-align: left; padding: 4px 6px; border-bottom: 1px solid #eee; }
          th { width: 45%; color: #333; }
          .meta { color: #555; font-size: 13px; }
        </style></head><body>
        <h1>$name</h1>
        <p class="meta">Ticker: <b>$ticker</b> · Index: $index · Sector: $sector</p>
        <h2>NAIC-analyse</h2>$scoreBlock
        <h2>Koers</h2>$priceBlock
        <h2>Fundamenten</h2>$fundBlock
        <p class="meta">NAIC EU — geen beleggingsadvies</p>
        </body></html>
    """.trimIndent()
}

private fun row(label: String, value: String): String =
    "<tr><th>${escape(label)}</th><td>$value</td></tr>"

private fun escape(text: String): String =
    text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

private fun fmt(value: Double): String = String.format(Locale.US, "%.2f", value)

private fun fmtLarge(value: Double): String = String.format(Locale.US, "%,.0f", value)
