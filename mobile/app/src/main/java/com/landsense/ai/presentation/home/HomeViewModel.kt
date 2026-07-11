package com.landsense.ai.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.repository.ObservationRepository
import com.landsense.ai.util.NetworkMonitor
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeState(
    val isBackendOnline: Boolean? = null, // null = checking, true = online, false = offline
    val isNetworkAvailable: Boolean = true
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: ObservationRepository,
    private val networkMonitor: NetworkMonitor
) : ViewModel() {

    private val _state = MutableStateFlow(HomeState())
    val state: StateFlow<HomeState> = _state.asStateFlow()

    init {
        checkBackend()
        
        viewModelScope.launch {
            networkMonitor.isOnline.collect { isOnline ->
                val wasOffline = !_state.value.isNetworkAvailable
                _state.update { it.copy(isNetworkAvailable = isOnline) }
                if (isOnline && wasOffline) {
                    checkBackend()
                }
            }
        }
    }

    fun checkBackend() {
        viewModelScope.launch {
            _state.update { it.copy(isBackendOnline = null) }
            repository.checkHealth()
                .onSuccess { _state.update { it.copy(isBackendOnline = true) } }
                .onFailure { _state.update { it.copy(isBackendOnline = false) } }
        }
    }
}
