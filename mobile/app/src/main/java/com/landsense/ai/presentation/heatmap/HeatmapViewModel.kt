package com.landsense.ai.presentation.heatmap

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.network.HeatmapPoint
import com.landsense.ai.data.repository.ObservationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class HeatmapFilter {
    ALL, HEAVY, STANDARD, COMPLETED
}

data class HeatmapState(
    val isLoading: Boolean = true,
    val allPoints: List<HeatmapPoint> = emptyList(),
    val points: List<HeatmapPoint> = emptyList(),
    val errorMessage: String? = null,
    val selectedFilter: HeatmapFilter = HeatmapFilter.ALL
)

@HiltViewModel
class HeatmapViewModel @Inject constructor(
    private val repository: ObservationRepository
) : ViewModel() {

    private val _state = MutableStateFlow(HeatmapState())
    val state: StateFlow<HeatmapState> = _state.asStateFlow()

    init {
        loadHeatmap()
    }

    fun loadHeatmap() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            repository.getHeatmap()
                .onSuccess { points ->
                    _state.value = _state.value.copy(
                        isLoading = false,
                        allPoints = points,
                        points = applyFilter(points, _state.value.selectedFilter),
                        errorMessage = null
                    )
                }
                .onFailure { err ->
                    _state.value = _state.value.copy(
                        isLoading = false,
                        errorMessage = "Could not load heatmap: ${err.localizedMessage}"
                    )
                }
        }
    }

    fun setFilter(filter: HeatmapFilter) {
        val allPts = _state.value.allPoints
        _state.value = _state.value.copy(
            selectedFilter = filter,
            points = applyFilter(allPts, filter)
        )
    }

    private fun applyFilter(points: List<HeatmapPoint>, filter: HeatmapFilter): List<HeatmapPoint> {
        return when (filter) {
            HeatmapFilter.ALL -> points
            HeatmapFilter.COMPLETED -> points.filter { it.stage?.lowercase()?.contains("complet") == true }
            HeatmapFilter.HEAVY -> points.filter { it.developmentScore >= 70 && !(it.stage?.lowercase()?.contains("complet") == true) }
            HeatmapFilter.STANDARD -> points.filter { it.developmentScore < 70 && !(it.stage?.lowercase()?.contains("complet") == true) }
        }
    }
}
