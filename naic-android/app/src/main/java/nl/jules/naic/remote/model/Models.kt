package nl.jules.naic.remote.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class HealthResponse(
    val status: String,
    val database: String? = null,
    val instruments: Int? = null,
    @Json(name = "naic_scores") val naicScores: Int? = null,
    @Json(name = "latest_score_date") val latestScoreDate: String? = null,
)

@JsonClass(generateAdapter = true)
data class RankingItem(
    val ticker: String,
    val name: String? = null,
    val exchange: String? = null,
    @Json(name = "index_code") val indexCode: String,
    @Json(name = "as_of_date") val asOfDate: String? = null,
    @Json(name = "current_price") val currentPrice: Double? = null,
    @Json(name = "win_loss_ratio") val winLossRatio: Double? = null,
    val advice: String,
    @Json(name = "total_return_5y_pct") val totalReturn5yPct: Double? = null,
    @Json(name = "revenue_cagr_10y") val revenueCagr10y: Double? = null,
    @Json(name = "eps_cagr_10y") val epsCagr10y: Double? = null,
    @Json(name = "buy_threshold") val buyThreshold: Double? = null,
    @Json(name = "hold_threshold") val holdThreshold: Double? = null,
)

@JsonClass(generateAdapter = true)
data class InstrumentDetailResponse(
    val instrument: Instrument,
    @Json(name = "naic_score") val naicScore: NaicScore? = null,
    val fundamentals: List<Fundamental> = emptyList(),
)

@JsonClass(generateAdapter = true)
data class Instrument(
    val id: Int? = null,
    val ticker: String,
    val exchange: String? = null,
    val isin: String? = null,
    val name: String? = null,
    val currency: String? = null,
    @Json(name = "yahoo_symbol") val yahooSymbol: String? = null,
    @Json(name = "stooq_symbol") val stooqSymbol: String? = null,
    val sector: String? = null,
    val country: String? = null,
    @Json(name = "index_code") val indexCode: String? = null,
    @Json(name = "weight_pct") val weightPct: Double? = null,
)

@JsonClass(generateAdapter = true)
data class NaicScore(
    @Json(name = "as_of_date") val asOfDate: String? = null,
    @Json(name = "current_price") val currentPrice: Double? = null,
    @Json(name = "price_high_10y") val priceHigh10y: Double? = null,
    @Json(name = "price_low_10y") val priceLow10y: Double? = null,
    @Json(name = "buy_threshold") val buyThreshold: Double? = null,
    @Json(name = "hold_threshold") val holdThreshold: Double? = null,
    val upside: Double? = null,
    val downside: Double? = null,
    @Json(name = "win_loss_ratio") val winLossRatio: Double? = null,
    val advice: String? = null,
    @Json(name = "total_return_5y_pct") val totalReturn5yPct: Double? = null,
    @Json(name = "revenue_cagr_10y") val revenueCagr10y: Double? = null,
    @Json(name = "eps_cagr_10y") val epsCagr10y: Double? = null,
    @Json(name = "equity_cagr_10y") val equityCagr10y: Double? = null,
)

@JsonClass(generateAdapter = true)
data class Fundamental(
    @Json(name = "fiscal_year") val fiscalYear: Int,
    val revenue: Double? = null,
    @Json(name = "net_income") val netIncome: Double? = null,
    val eps: Double? = null,
    @Json(name = "equity_per_share") val equityPerShare: Double? = null,
)

@JsonClass(generateAdapter = true)
data class PricePoint(
    @Json(name = "trade_date") val tradeDate: String,
    val open: Double? = null,
    val high: Double? = null,
    val low: Double? = null,
    val close: Double? = null,
    @Json(name = "adj_close") val adjClose: Double? = null,
    val volume: Double? = null,
)

enum class IndexTab(val label: String, val apiCode: String?) {
    AEX("AEX", "AEX"),
    BEL20("BEL 20", "BEL20"),
    ALL("Alles", null),
}

enum class AdviceZone(val code: String, val label: String) {
    KOOP("K", "Koop (K)"),
    NEUTRAAL("n", "Neutraal (n)"),
    VERMIJDEN("v", "Vermijden (v)"),
}

fun groupByZone(items: List<RankingItem>): Map<AdviceZone, List<RankingItem>> =
    AdviceZone.entries.associateWith { zone ->
        items.filter { it.advice == zone.code }
    }
