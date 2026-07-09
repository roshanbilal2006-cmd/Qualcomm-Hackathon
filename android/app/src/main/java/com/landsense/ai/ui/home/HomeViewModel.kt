package com.landsense.ai.ui.home

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * HomeViewModel — Minimal state for the home screen.
 * Extended in the future to show quick stats / last scan summary.
 */
class HomeViewModel : ViewModel() {
    // Placeholder for future quick-stats state
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
}

data class HomeUiState(
    val isLoading: Boolean = false
)
