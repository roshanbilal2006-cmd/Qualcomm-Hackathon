package com.landsense.ai.ui.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.model.HistoryEntry
import com.landsense.ai.data.repository.ObservationRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class HistoryViewModel(
    private val repository: ObservationRepository = ObservationRepository()
) : ViewModel() {

    private val _uiState = MutableStateFlow(HistoryUiState())
    val uiState: StateFlow<HistoryUiState> = _uiState.asStateFlow()

    init { loadHistory() }

    fun loadHistory() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.getHistory().fold(
                onSuccess = { entries ->
                    _uiState.update { it.copy(isLoading = false, entries = entries) }
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

data class HistoryUiState(
    val isLoading : Boolean           = false,
    val entries   : List<HistoryEntry> = emptyList(),
    val error     : String?           = null
)
