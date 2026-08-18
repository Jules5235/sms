package nl.jules.naic.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import nl.jules.naic.remote.model.AdviceZone
import nl.jules.naic.remote.model.IndexTab
import nl.jules.naic.remote.model.RankingItem
import nl.jules.naic.remote.model.groupByZone
import nl.jules.naic.remote.repository.NaicRepository

data class HomeUiState(
    val selectedTab: IndexTab = IndexTab.AEX,
    val isLoading: Boolean = true,
    val error: String? = null,
    val latestScoreDate: String? = null,
    val zones: Map<AdviceZone, List<RankingItem>> = emptyMap(),
)

class RankingViewModel(
    private val repository: NaicRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun selectTab(tab: IndexTab) {
        if (tab == _uiState.value.selectedTab) return
        _uiState.update { it.copy(selectedTab = tab) }
        loadRanking(tab)
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val health = repository.health()
                loadRanking(_uiState.value.selectedTab, health.latestScoreDate)
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

    private fun loadRanking(tab: IndexTab, scoreDate: String? = _uiState.value.latestScoreDate) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val items = repository.loadRanking(tab)
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        latestScoreDate = scoreDate,
                        zones = groupByZone(items),
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
