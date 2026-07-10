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

data class HeatmapState(
    val isLoading: Boolean = true,
    val points: List<HeatmapPoint> = emptyList(),
    val errorMessage: String? = null
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
            _state.value = HeatmapState(isLoading = true)
            // Backend's /heatmap first tries the cloud layer (port 8003), then falls back to local SQLite
            repository.getHeatmap()
                .onSuccess { points ->
                    _state.value = HeatmapState(isLoading = false, points = points)
                }
                .onFailure { err ->
                    _state.value = HeatmapState(isLoading = false, errorMessage = "Could not load heatmap: ${err.localizedMessage}")
                }
        }
    }
}
