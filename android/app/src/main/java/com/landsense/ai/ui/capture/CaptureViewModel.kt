package com.landsense.ai.ui.capture

import android.content.Context
import android.location.Location
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.model.ObservationRequest
import com.landsense.ai.data.model.ObservationResponse
import com.landsense.ai.data.repository.ObservationRepository
import com.landsense.ai.util.GpsHelper
import com.landsense.ai.util.ImageUtils
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.Instant

/**
 * CaptureViewModel — Orchestrates image collection, GPS capture, and submission.
 *
 * MVVM contract:
 * - ViewModel owns all state.
 * - CaptureScreen only reads state and delegates events here.
 * - Repository is the only Backend-communication path.
 */
class CaptureViewModel(
    private val repository: ObservationRepository = ObservationRepository()
) : ViewModel() {

    private val _uiState = MutableStateFlow(CaptureUiState())
    val uiState: StateFlow<CaptureUiState> = _uiState.asStateFlow()

    // ─── Image Management ─────────────────────────────────────────────────────

    /** Called by CaptureScreen when a photo is taken for a given slot. */
    fun onImageCaptured(slot: ImageSlot, uri: Uri) {
        _uiState.update { state ->
            state.copy(capturedImages = state.capturedImages + (slot to uri))
        }
    }

    fun removeImage(slot: ImageSlot) {
        _uiState.update { state ->
            state.copy(capturedImages = state.capturedImages - slot)
        }
    }

    // ─── Voice Input ──────────────────────────────────────────────────────────

    fun onVoiceTranscript(transcript: String) {
        _uiState.update { it.copy(voiceQuery = transcript) }
    }

    fun clearVoiceQuery() {
        _uiState.update { it.copy(voiceQuery = "") }
    }

    // ─── GPS ──────────────────────────────────────────────────────────────────

    fun captureGps(context: Context) {
        viewModelScope.launch {
            try {
                val location: Location = GpsHelper.getCurrentLocation(context)
                _uiState.update {
                    it.copy(
                        latitude    = location.latitude,
                        longitude   = location.longitude,
                        gpsAccuracy = location.accuracy,
                        gpsError    = null
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(gpsError = e.message) }
            }
        }
    }

    // ─── Submission ───────────────────────────────────────────────────────────

    fun submitObservation(
        context: Context,
        onSuccess: (ObservationResponse) -> Unit
    ) {
        val state = _uiState.value
        if (state.capturedImages.isEmpty()) {
            _uiState.update { it.copy(submissionError = "Please capture at least one image.") }
            return
        }
        if (state.latitude == null || state.longitude == null) {
            _uiState.update { it.copy(submissionError = "GPS not yet captured. Please wait.") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isSubmitting = true, submissionError = null) }

            // Encode images to Base64
            val base64Images = state.capturedImages.values.mapNotNull { uri ->
                try { ImageUtils.uriToBase64(context, uri) } catch (e: Exception) { null }
            }

            val request = ObservationRequest(
                images      = base64Images,
                latitude    = state.latitude,
                longitude   = state.longitude,
                timestamp   = Instant.now().toString(),
                voiceQuery  = state.voiceQuery,
                device      = "OnePlus15"
            )

            val result = repository.submitObservation(request)
            result.fold(
                onSuccess = { response ->
                    _uiState.update { it.copy(isSubmitting = false) }
                    onSuccess(response)
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(
                            isSubmitting    = false,
                            submissionError = error.message ?: "Unable to connect."
                        )
                    }
                }
            )
        }
    }

    fun clearError() {
        _uiState.update { it.copy(submissionError = null) }
    }
}

/** The four directed image slots. */
enum class ImageSlot(val label: String, val emoji: String) {
    FRONT("Front", "🔼"),
    BACK ("Back",  "🔽"),
    LEFT ("Left",  "◀"),
    RIGHT("Right", "▶")
}

data class CaptureUiState(
    val capturedImages  : Map<ImageSlot, Uri> = emptyMap(),
    val voiceQuery      : String    = "",
    val latitude        : Double?   = null,
    val longitude       : Double?   = null,
    val gpsAccuracy     : Float?    = null,
    val gpsError        : String?   = null,
    val isSubmitting    : Boolean   = false,
    val submissionError : String?   = null
)
