package com.landsense.ai.presentation.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.network.ObservationResponse
import com.landsense.ai.data.repository.ObservationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HistoryState(
    val isLoading: Boolean = true,
    val observations: List<ObservationResponse> = emptyList(),
    val errorMessage: String? = null
)

@HiltViewModel
class HistoryViewModel @Inject constructor(
    private val repository: ObservationRepository
) : ViewModel() {

    private val _state = MutableStateFlow(HistoryState())
    val state: StateFlow<HistoryState> = _state.asStateFlow()

    init {
        loadHistory()
    }

    fun loadHistory() {
        viewModelScope.launch {
            _state.value = HistoryState(isLoading = true)
            repository.getHistory(ownerId = "android-device-001")
                .onSuccess { list ->
                    _state.value = HistoryState(isLoading = false, observations = list)
                }
                .onFailure { err ->
                    _state.value = HistoryState(isLoading = false, errorMessage = "Could not load history: ${err.localizedMessage}")
                }
        }
    }
}
