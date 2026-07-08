package com.landsense.ai.presentation.capture

import android.location.Location
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.network.ObservationRequest
import com.landsense.ai.data.repository.ObservationRepository
import com.landsense.ai.util.LocationTracker
import dagger.hilt.android.lifecycle.HiltViewModel
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
    val location: Location? = null
)

@HiltViewModel
class CaptureViewModel @Inject constructor(
    private val repository: ObservationRepository,
    private val locationTracker: LocationTracker
) : ViewModel() {

    private val _state = MutableStateFlow(CaptureState())
    val state: StateFlow<CaptureState> = _state.asStateFlow()

    fun addImage(base64Image: String) {
        _state.update { it.copy(images = it.images + base64Image) }
    }

    fun setVoiceQuery(query: String) {
        _state.update { it.copy(voiceQuery = query) }
    }
    
    fun clearError() {
        _state.update { it.copy(errorMessage = null) }
    }

    fun submitObservation() {
        viewModelScope.launch {
            _state.update { it.copy(isUploading = true, errorMessage = null) }
            
            // 1. Fetch Location
            val location = locationTracker.getCurrentLocation()
            _state.update { it.copy(location = location) }

            if (location == null) {
                _state.update { 
                    it.copy(isUploading = false, errorMessage = "Location unavailable. Please check permissions and GPS.") 
                }
                return@launch
            }

            // 2. Prepare Request
            val request = ObservationRequest(
                images = _state.value.images,
                latitude = location.latitude.toString(),
                longitude = location.longitude.toString(),
                timestamp = Instant.now().toString(),
                voice_query = _state.value.voiceQuery
            )

            // 3. Submit
            val result = repository.submitObservation(request)
            result.onSuccess { response ->
                _state.update { it.copy(isUploading = false, uploadSuccess = true) }
                // In a real app we would pass the response to the result screen via navigation arguments or a shared ViewModel
            }.onFailure { error ->
                _state.update { 
                    it.copy(isUploading = false, errorMessage = "Unable to connect. ${error.localizedMessage}") 
                }
            }
        }
    }
}
