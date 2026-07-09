package com.landsense.ai.presentation.capture

import android.location.Location
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.network.ObservationRequest
import com.landsense.ai.data.network.VisionData
import com.landsense.ai.data.repository.ObservationRepository
import com.landsense.ai.data.repository.SettingsRepository
import com.landsense.ai.util.LocationTracker
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.Instant
import javax.inject.Inject

data class CaptureState(
    val images: List<String> = emptyList(),
    val isUploading: Boolean = false,
    val uploadSuccess: Boolean = false,
    val errorMessage: String? = null,
    val voiceQuery: String? = null,
    val location: Location? = null,
    val isModeBEnabled: Boolean = false,
    val vlmProcessingStatus: String? = null // To show "Running LiteRT VLM on-device..." text
)

@HiltViewModel
class CaptureViewModel @Inject constructor(
    private val repository: ObservationRepository,
    private val locationTracker: LocationTracker,
    private val settingsRepository: SettingsRepository
) : ViewModel() {

    private val _state = MutableStateFlow(CaptureState(isModeBEnabled = settingsRepository.isModeBEnabled()))
    val state: StateFlow<CaptureState> = _state.asStateFlow()

    fun addImage(base64Image: String) {
        _state.update { it.copy(images = it.images + base64Image) }
    }

    fun setVoiceQuery(query: String) {
        _state.update { it.copy(voiceQuery = query) }
    }
    
    fun toggleModeB(enabled: Boolean) {
        settingsRepository.setModeBEnabled(enabled)
        _state.update { it.copy(isModeBEnabled = enabled) }
    }
    
    fun clearError() {
        _state.update { it.copy(errorMessage = null) }
    }

    fun submitObservation() {
        viewModelScope.launch {
            _state.update { it.copy(isUploading = true, errorMessage = null, vlmProcessingStatus = null) }
            
            // 1. Fetch Location
            val location = locationTracker.getCurrentLocation()
            _state.update { it.copy(location = location) }

            if (location == null) {
                _state.update { 
                    it.copy(isUploading = false, errorMessage = "Location unavailable. Please check permissions and GPS.") 
                }
                return@launch
            }

            var imagesToSend = _state.value.images
            var visionData: VisionData? = null

            // 2. Prepare Payload (Mode A vs Mode B)
            if (_state.value.isModeBEnabled) {
                _state.update { it.copy(vlmProcessingStatus = "Running LiteRT/VLM on edge...") }
                // MOCK DELAY for on-device VLM processing
                delay(2500) 
                
                // In Mode B, images are not sent. Vision output is sent instead.
                imagesToSend = emptyList()
                visionData = VisionData(
                    source = "android_litert_vlm",
                    imageCount = _state.value.images.size.takeIf { it > 0 } ?: 4,
                    views = listOf("front", "back", "left", "right"),
                    constructionStage = "Structural Work",
                    progress = 65.0,
                    confidence = 0.91,
                    description = "Concrete frame, scaffolding, and active structural work visible.",
                    embedding = listOf(0.015, -0.024, 0.187)
                )
                _state.update { it.copy(vlmProcessingStatus = "Edge processing complete. Uploading to fusion backend...") }
            }

            val request = ObservationRequest(
                timestamp = Instant.now().toString(),
                ownerId = "android-device-001",
                latitude = location.latitude,
                longitude = location.longitude,
                images = imagesToSend,
                vision = visionData,
                voiceQuery = _state.value.voiceQuery
            )

            // 3. Submit
            val result = repository.submitObservation(request)
            result.onSuccess { response ->
                _state.update { it.copy(isUploading = false, uploadSuccess = true, vlmProcessingStatus = null) }
                // In a real app we pass response to ResultScreen via nav arguments
            }.onFailure { error ->
                _state.update { 
                    it.copy(isUploading = false, vlmProcessingStatus = null, errorMessage = "Unable to connect. ${error.localizedMessage}") 
                }
            }
        }
    }
}
