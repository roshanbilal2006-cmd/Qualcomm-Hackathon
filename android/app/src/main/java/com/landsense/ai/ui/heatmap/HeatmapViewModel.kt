package com.landsense.ai.ui.heatmap

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.model.HeatmapPoint
import com.landsense.ai.data.repository.ObservationRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class HeatmapViewModel(
    private val repository: ObservationRepository = ObservationRepository()
) : ViewModel() {

    private val _uiState = MutableStateFlow(HeatmapUiState())
    val uiState: StateFlow<HeatmapUiState> = _uiState.asStateFlow()

    init { loadHeatmap() }

    fun loadHeatmap() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.getHeatmap().fold(
                onSuccess = { points ->
                    _uiState.update { it.copy(isLoading = false, points = points) }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message ?: "Unable to connect.")
                    }
                }
            )
        }
    }
}

data class HeatmapUiState(
    val isLoading : Boolean           = false,
    val points    : List<HeatmapPoint> = emptyList(),
    val error     : String?           = null
)
