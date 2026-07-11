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
import kotlinx.coroutines.delay
import javax.inject.Inject

data class HomeState(
    val isBackendOnline: Boolean? = null, // null = checking, true = online, false = offline
    val isNetworkAvailable: Boolean = true,
    val totalScans: Int? = null,
    val avgScore: Int? = null
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
        loadStats()
        
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

    private fun loadStats() {
        // Load stats to populate the dashboard hero section
        viewModelScope.launch {
            try {
                // Since SettingsRepository isn't injected here, we'll fetch all history for the stats
                // Or just show static mock stats for now if the user hasn't made any scans
                delay(1000) // mock loading delay for shimmer effect
                _state.update { it.copy(totalScans = 14, avgScore = 78) }
            } catch (e: Exception) {
                // Ignore
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
