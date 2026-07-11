package com.landsense.ai.presentation.capture

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
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
import java.io.ByteArrayOutputStream
import java.time.Instant
import java.util.concurrent.Executors
import javax.inject.Inject

data class CaptureState(
    val images: List<String> = emptyList(),         // base64 data URIs ready for backend
    val imageThumbnails: List<ByteArray> = emptyList(), // compressed JPEG bytes for preview
    val isCapturing: Boolean = false,
    val isUploading: Boolean = false,
    val uploadSuccess: Boolean = false,
    val successObservationId: String? = null,       // passed to ResultScreen after upload
    val errorMessage: String? = null,
    val voiceQuery: String? = null,
    val isRecording: Boolean = false,
    val location: Location? = null,
    val uploadStatusText: String? = null
)

private const val MAX_IMAGES = 4
private const val MAX_IMAGE_SIDE = 1024
private const val JPEG_QUALITY = 80

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
                        try {
                            val jpegBytes = imageProxyToCompressedJpeg(image)
                            image.close()
                            val base64 = Base64.encodeToString(jpegBytes, Base64.NO_WRAP)
                            val dataUri = "data:image/jpeg;base64,$base64"
                            _state.update { current ->
                                current.copy(
                                    images = current.images + dataUri,
                                    imageThumbnails = current.imageThumbnails + jpegBytes,
                                    isCapturing = false
                                )
                            }
                        } catch (e: Exception) {
                            _state.update {
                                it.copy(isCapturing = false, errorMessage = "Image processing failed: ${e.localizedMessage}")
                            }
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

    fun setVoiceQuery(query: String?) {
        _state.update { it.copy(voiceQuery = query) }
    }

    fun setRecording(recording: Boolean) {
        _state.update { it.copy(isRecording = recording) }
    }

    fun clearVoiceQuery() {
        _state.update { it.copy(voiceQuery = null) }
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
            val ownerId = settingsRepository.getOwnerId()
            val request = ObservationRequest(
                timestamp = Instant.now().toString(),
                ownerId = ownerId,
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

    /**
     * Converts an ImageProxy to a properly compressed, resized JPEG byte array.
     *
     * The previous implementation just read raw plane bytes which produced corrupt/unreadable
     * images. This version:
     * 1. Decodes the image planes into a Bitmap
     * 2. Applies rotation correction from EXIF data
     * 3. Resizes so the longest side is max 1024px
     * 4. Compresses to JPEG at quality 80
     */
    private suspend fun imageProxyToCompressedJpeg(image: ImageProxy): ByteArray =
        withContext(Dispatchers.Default) {
            // Step 1: Convert ImageProxy planes to a Bitmap
            val buffer = image.planes[0].buffer
            val rawBytes = ByteArray(buffer.remaining())
            buffer.get(rawBytes)

            var bitmap = BitmapFactory.decodeByteArray(rawBytes, 0, rawBytes.size)

            // If BitmapFactory can't decode (e.g. YUV format), fall back to NV21 → JPEG approach
            if (bitmap == null) {
                // For YUV_420_888 format, use the JPEG output directly from planes
                // This typically happens with camera2 — CameraX usually provides JPEG
                throw IllegalStateException("Failed to decode captured image. Ensure CameraX is configured for JPEG output.")
            }

            // Step 2: Apply rotation from ImageProxy metadata
            val rotation = image.imageInfo.rotationDegrees
            if (rotation != 0) {
                val matrix = Matrix().apply { postRotate(rotation.toFloat()) }
                bitmap = Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
            }

            // Step 3: Resize so the longest side is max MAX_IMAGE_SIDE px
            val width = bitmap.width
            val height = bitmap.height
            val longestSide = maxOf(width, height)
            if (longestSide > MAX_IMAGE_SIDE) {
                val scale = MAX_IMAGE_SIDE.toFloat() / longestSide
                val newWidth = (width * scale).toInt()
                val newHeight = (height * scale).toInt()
                bitmap = Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
            }

            // Step 4: Compress to JPEG
            val outputStream = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.JPEG, JPEG_QUALITY, outputStream)
            outputStream.toByteArray()
        }

    override fun onCleared() {
        super.onCleared()
        executor.shutdown()
    }
}

