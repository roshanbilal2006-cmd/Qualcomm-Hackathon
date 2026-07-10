package com.landsense.ai.presentation.capture

import android.content.Context
import android.location.Location
import android.util.Base64
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.network.ObservationRequest
import com.landsense.ai.data.repository.ObservationRepository
import com.landsense.ai.data.repository.SettingsRepository
import com.landsense.ai.util.LocationTracker
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.concurrent.Executors
import javax.inject.Inject

data class CaptureState(
    val images: List<String> = emptyList(),         // base64 data URIs ready for backend
    val imageThumbnails: List<ByteArray> = emptyList(), // raw bytes for preview display
    val isCapturing: Boolean = false,
    val isUploading: Boolean = false,
    val uploadSuccess: Boolean = false,
    val successObservationId: String? = null,       // passed to ResultScreen after upload
    val errorMessage: String? = null,
    val voiceQuery: String? = null,
    val location: Location? = null,
    val uploadStatusText: String? = null
)

private const val OWNER_ID = "android-device-001"
private const val MAX_IMAGES = 4

@HiltViewModel
class CaptureViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val repository: ObservationRepository,
    private val locationTracker: LocationTracker,
    private val settingsRepository: SettingsRepository
) : ViewModel() {

    private val _state = MutableStateFlow(CaptureState())
    val state: StateFlow<CaptureState> = _state.asStateFlow()

    private val executor = Executors.newSingleThreadExecutor()

    fun capturePhoto(imageCapture: ImageCapture) {
        if (_state.value.images.size >= MAX_IMAGES || _state.value.isCapturing) return
        _state.update { it.copy(isCapturing = true) }

        imageCapture.takePicture(
            executor,
            object : ImageCapture.OnImageCapturedCallback() {
                override fun onCaptureSuccess(image: ImageProxy) {
                    viewModelScope.launch(Dispatchers.Default) {
                        val bytes = imageProxyToByteArray(image)
                        image.close()
                        val base64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
                        val dataUri = "data:image/jpeg;base64,$base64"
                        _state.update { current ->
                            current.copy(
                                images = current.images + dataUri,
                                imageThumbnails = current.imageThumbnails + bytes,
                                isCapturing = false
                            )
                        }
                    }
                }

                override fun onError(exception: ImageCaptureException) {
                    _state.update { it.copy(isCapturing = false, errorMessage = "Capture failed: ${exception.localizedMessage}") }
                }
            }
        )
    }

    fun removeImage(index: Int) {
        _state.update { current ->
            current.copy(
                images = current.images.toMutableList().also { it.removeAt(index) },
                imageThumbnails = current.imageThumbnails.toMutableList().also { it.removeAt(index) }
            )
        }
    }

    fun setVoiceQuery(query: String) {
        _state.update { it.copy(voiceQuery = query) }
    }

    fun clearError() {
        _state.update { it.copy(errorMessage = null) }
    }

    fun submitObservation() {
        viewModelScope.launch {
            _state.update { it.copy(isUploading = true, errorMessage = null, uploadStatusText = "Getting GPS location...") }

            // 1. Fetch Location
            val location = locationTracker.getCurrentLocation()
            if (location == null) {
                _state.update {
                    it.copy(isUploading = false, uploadStatusText = null, errorMessage = "Location unavailable. Enable GPS and try again.")
                }
                return@launch
            }
            _state.update { it.copy(location = location, uploadStatusText = "Sending to backend...") }

            // 2. Build request — images already in "data:image/jpeg;base64,..." format
            val request = ObservationRequest(
                timestamp = Instant.now().toString(),
                ownerId = OWNER_ID,
                latitude = location.latitude,
                longitude = location.longitude,
                images = _state.value.images,
                voiceQuery = _state.value.voiceQuery
            )

            // 3. Submit
            val result = repository.submitObservation(request)
            result.onSuccess { response ->
                _state.update {
                    it.copy(
                        isUploading = false,
                        uploadSuccess = true,
                        uploadStatusText = null,
                        successObservationId = response.observationId
                    )
                }
            }.onFailure { error ->
                _state.update {
                    it.copy(
                        isUploading = false,
                        uploadStatusText = null,
                        errorMessage = "Backend unreachable. Check IP in Settings. ${error.localizedMessage}"
                    )
                }
            }
        }
    }

    private suspend fun imageProxyToByteArray(image: ImageProxy): ByteArray =
        withContext(Dispatchers.IO) {
            val buffer = image.planes[0].buffer
            val bytes = ByteArray(buffer.remaining())
            buffer.get(bytes)
            bytes
        }

    override fun onCleared() {
        super.onCleared()
        executor.shutdown()
    }
}
