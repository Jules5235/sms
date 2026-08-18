package nl.jules.naic.ui.detail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import nl.jules.naic.remote.model.Fundamental
import nl.jules.naic.remote.model.Instrument
import nl.jules.naic.remote.model.NaicScore
import nl.jules.naic.remote.model.PricePoint
import nl.jules.naic.remote.repository.NaicRepository

data class DetailUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val instrument: Instrument? = null,
    val naicScore: NaicScore? = null,
    val fundamentals: List<Fundamental> = emptyList(),
    val prices: List<PricePoint> = emptyList(),
)

class DetailViewModel(
    private val repository: NaicRepository,
    private val ticker: String,
) : ViewModel() {
    private val _uiState = MutableStateFlow(DetailUiState())
    val uiState: StateFlow<DetailUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val detailDeferred = async { repository.instrumentDetail(ticker) }
                val pricesDeferred = async { repository.instrumentPrices(ticker) }
                val detail = detailDeferred.await()
                val prices = pricesDeferred.await()
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        instrument = detail.instrument,
                        naicScore = detail.naicScore,
                        fundamentals = detail.fundamentals,
                        prices = prices,
                        error = null,
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Onbekende fout",
                    )
                }
            }
        }
    }
}
