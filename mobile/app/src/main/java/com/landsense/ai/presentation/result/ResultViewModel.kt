package com.landsense.ai.presentation.result

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

data class ResultState(
    val isLoading: Boolean = true,
    val observation: ObservationResponse? = null,
    val errorMessage: String? = null
)

@HiltViewModel
class ResultViewModel @Inject constructor(
    private val repository: ObservationRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ResultState())
    val state: StateFlow<ResultState> = _state.asStateFlow()

    fun loadObservation(observationId: String) {
        viewModelScope.launch {
            _state.value = ResultState(isLoading = true)
            repository.getObservationById(observationId)
                .onSuccess { obs ->
                    _state.value = ResultState(isLoading = false, observation = obs)
                }
                .onFailure { err ->
                    _state.value = ResultState(isLoading = false, errorMessage = "Could not load report: ${err.localizedMessage}")
                }
        }
    }
}
