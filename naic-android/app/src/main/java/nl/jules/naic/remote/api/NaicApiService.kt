package nl.jules.naic.remote.api

import nl.jules.naic.remote.model.HealthResponse
import nl.jules.naic.remote.model.InstrumentDetailResponse
import nl.jules.naic.remote.model.PricePoint
import nl.jules.naic.remote.model.RankingItem
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface NaicApiService {
    @GET("health")
    suspend fun health(): HealthResponse

    @GET("api/ranking/{indexCode}")
    suspend fun rankingByIndex(@Path("indexCode") indexCode: String): List<RankingItem>

    @GET("api/ranking")
    suspend fun ranking(
        @Query("index") index: String? = null,
        @Query("advice") advice: String? = null,
    ): List<RankingItem>

    @GET("api/instruments/{ticker}")
    suspend fun instrumentDetail(@Path("ticker") ticker: String): InstrumentDetailResponse

    @GET("api/instruments/{ticker}/prices")
    suspend fun instrumentPrices(
        @Path("ticker") ticker: String,
        @Query("limit") limit: Int = 365,
    ): List<PricePoint>
}
