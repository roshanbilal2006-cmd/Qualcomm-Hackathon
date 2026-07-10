package com.landsense.ai.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.repository.ObservationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeState(
    val isBackendOnline: Boolean? = null // null = checking, true = online, false = offline
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: ObservationRepository
) : ViewModel() {

    private val _state = MutableStateFlow(HomeState())
    val state: StateFlow<HomeState> = _state.asStateFlow()

    init {
        checkBackend()
    }

    fun checkBackend() {
        viewModelScope.launch {
            _state.value = HomeState(isBackendOnline = null)
            repository.checkHealth()
                .onSuccess { _state.value = HomeState(isBackendOnline = true) }
                .onFailure { _state.value = HomeState(isBackendOnline = false) }
        }
    }
}
