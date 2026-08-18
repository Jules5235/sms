package nl.jules.naic.remote.repository

import nl.jules.naic.remote.api.NaicApiService
import nl.jules.naic.remote.model.HealthResponse
import nl.jules.naic.remote.model.IndexTab
import nl.jules.naic.remote.model.InstrumentDetailResponse
import nl.jules.naic.remote.model.PricePoint
import nl.jules.naic.remote.model.RankingItem

class NaicRepository(
    private var api: NaicApiService,
) {
    fun updateApi(api: NaicApiService) {
        this.api = api
    }

    suspend fun health(): HealthResponse = api.health()

    suspend fun loadRanking(tab: IndexTab): List<RankingItem> = when (tab) {
        IndexTab.AEX -> api.rankingByIndex("AEX")
        IndexTab.BEL20 -> api.rankingByIndex("BEL20")
        IndexTab.ALL -> {
            val aex = api.rankingByIndex("AEX")
            val bel20 = api.rankingByIndex("BEL20")
            (aex + bel20).sortedWith(
                compareBy<RankingItem> { it.indexCode }
                    .thenBy { adviceOrder(it.advice) }
                    .thenByDescending { it.winLossRatio ?: 0.0 },
            )
        }
    }

    suspend fun instrumentDetail(ticker: String): InstrumentDetailResponse =
        api.instrumentDetail(ticker)

    suspend fun instrumentPrices(ticker: String, limit: Int = 365): List<PricePoint> =
        api.instrumentPrices(ticker, limit).reversed()

    private fun adviceOrder(advice: String): Int = when (advice) {
        "K" -> 0
        "n" -> 1
        else -> 2
    }
}
