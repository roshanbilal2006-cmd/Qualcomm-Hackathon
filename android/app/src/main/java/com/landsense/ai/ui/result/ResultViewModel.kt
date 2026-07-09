package com.landsense.ai.ui.result

import androidx.lifecycle.ViewModel
import com.landsense.ai.data.model.ObservationResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * ResultViewModel — Holds the observation result passed from the Capture screen.
 */
class ResultViewModel : ViewModel() {
    private val _observation = MutableStateFlow<ObservationResponse?>(null)
    val observation: StateFlow<ObservationResponse?> = _observation.asStateFlow()

    fun setObservation(obs: ObservationResponse) {
        _observation.value = obs
    }
}
