package com.landsense.ai.ui.capture

import android.content.ContentValues
import android.content.Context
import android.provider.MediaStore
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.widget.LinearLayout
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import com.landsense.ai.data.model.ObservationResponse
import com.landsense.ai.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

/**
 * CaptureScreen — Full-screen CameraX preview with 4-angle image capture.
 *
 * Flow:
 *  1. App auto-captures GPS on first composition.
 *  2. User taps a slot (Front/Back/Left/Right) to set the active capture target.
 *  3. Shutter button captures photo → stored in the slot.
 *  4. Optional: mic FAB opens voice input.
 *  5. Submit sends everything to backend via ViewModel.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    onObservationSubmitted: (ObservationResponse) -> Unit,
    viewModel: CaptureViewModel = viewModel()
) {
    val context       = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val uiState by viewModel.uiState.collectAsState()

    // Voice helper — bound to this composable's lifecycle
    val voiceHelper = remember { VoiceInputHelper(context) }
    val voiceTranscript by voiceHelper.transcript.collectAsState()
    val isListening     by voiceHelper.isListening.collectAsState()
    val voiceError      by voiceHelper.error.collectAsState()

    // Pass transcript back to ViewModel
    LaunchedEffect(voiceTranscript) {
        if (voiceTranscript.isNotBlank()) viewModel.onVoiceTranscript(voiceTranscript)
    }

    // Auto-capture GPS on entry
    LaunchedEffect(Unit) {
        viewModel.captureGps(context)
    }

    DisposableEffect(Unit) {
        onDispose { voiceHelper.destroy() }
    }

    // CameraX state
    var imageCapture: ImageCapture? by remember { mutableStateOf(null) }
    var activeSlot by remember { mutableStateOf(ImageSlot.FRONT) }

    Box(modifier = Modifier.fillMaxSize().background(Surface900)) {

        // ─── Camera Preview ───────────────────────────────────────────────
        AndroidView(
            factory = { ctx ->
                PreviewView(ctx).apply {
                    layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
                    scaleType    = PreviewView.ScaleType.FILL_CENTER
                }
            },
            modifier = Modifier.fillMaxSize(),
            update = { previewView ->
                val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    val capture = ImageCapture.Builder()
                        .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                        .build()
                    imageCapture = capture
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        lifecycleOwner,
                        CameraSelector.DEFAULT_BACK_CAMERA,
                        preview,
                        capture
                    )
                }, ContextCompat.getMainExecutor(context))
            }
        )

        // ─── Top: GPS Status + Back ───────────────────────────────────────
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .statusBarsPadding()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment     = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(50.dp),
                color = Surface800.copy(alpha = 0.85f)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Filled.LocationOn,
                        contentDescription = "GPS",
                        tint  = if (uiState.latitude != null) HeatLow else HeatHigh,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text  = if (uiState.latitude != null)
                            "GPS ✓  ${String.format("%.4f", uiState.latitude)}, ${String.format("%.4f", uiState.longitude)}"
                        else uiState.gpsError ?: "Acquiring GPS…",
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurface
                    )
                }
            }
        }

        // ─── Image Slot Indicators ────────────────────────────────────────
        Row(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 80.dp)
                .padding(horizontal = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            ImageSlot.values().forEach { slot ->
                val isCaptured = slot in uiState.capturedImages
                val isActive   = slot == activeSlot
                Surface(
                    modifier = Modifier
                        .weight(1f)
                        .height(44.dp)
                        .clickable { activeSlot = slot },
                    shape = RoundedCornerShape(10.dp),
                    color = when {
                        isCaptured -> HeatLow.copy(alpha = 0.25f)
                        isActive   -> Sapphire500.copy(alpha = 0.25f)
                        else       -> Surface800.copy(alpha = 0.75f)
                    },
                    border = androidx.compose.foundation.BorderStroke(
                        width = 1.5.dp,
                        color = when {
                            isCaptured -> HeatLow
                            isActive   -> Sapphire500
                            else       -> Surface600
                        }
                    )
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(slot.emoji, style = MaterialTheme.typography.labelSmall)
                            Text(
                                text  = slot.label,
                                style = MaterialTheme.typography.labelSmall,
                                color = if (isCaptured) HeatLow
                                        else if (isActive) Sapphire500
                                        else OnSurfaceMuted
                            )
                        }
                    }
                }
            }
        }

        // ─── Bottom Controls ──────────────────────────────────────────────
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .navigationBarsPadding()
                .padding(bottom = 24.dp, start = 24.dp, end = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            // Voice transcript display
            if (uiState.voiceQuery.isNotBlank()) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape    = RoundedCornerShape(12.dp),
                    color    = Surface800.copy(alpha = 0.9f)
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Filled.Mic, null,
                            tint = Sapphire500, modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = uiState.voiceQuery,
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurface,
                            modifier = Modifier.weight(1f)
                        )
                        IconButton(
                            onClick = { viewModel.clearVoiceQuery(); voiceHelper.clearTranscript() },
                            modifier = Modifier.size(20.dp)
                        ) {
                            Icon(Icons.Filled.Close, null, tint = OnSurfaceMuted,
                                modifier = Modifier.size(14.dp))
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
            }

            // Error display
            if (uiState.submissionError != null) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape    = RoundedCornerShape(10.dp),
                    color    = HeatHigh.copy(alpha = 0.15f)
                ) {
                    Row(
                        modifier = Modifier.padding(10.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Filled.Warning, null, tint = HeatHigh,
                            modifier = Modifier.size(14.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text  = uiState.submissionError ?: "",
                            style = MaterialTheme.typography.labelSmall,
                            color = HeatHigh
                        )
                    }
                }
                Spacer(modifier = Modifier.height(10.dp))
            }

            // Shutter + Voice + Submit row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                // Mic FAB
                FloatingActionButton(
                    onClick = {
                        if (isListening) voiceHelper.stopListening()
                        else voiceHelper.startListening()
                    },
                    modifier          = Modifier.size(52.dp),
                    containerColor    = if (isListening) Sapphire500 else Surface700,
                    contentColor      = OnSurface,
                    shape             = CircleShape,
                    elevation         = FloatingActionButtonDefaults.elevation(0.dp)
                ) {
                    Icon(
                        imageVector        = if (isListening) Icons.Filled.MicOff else Icons.Filled.Mic,
                        contentDescription = "Voice input",
                        modifier           = Modifier.size(22.dp)
                    )
                }

                // Shutter button
                Box(
                    modifier = Modifier
                        .size(76.dp)
                        .border(3.dp, Sapphire500, CircleShape)
                        .padding(6.dp)
                        .background(Color.White, CircleShape)
                        .clickable {
                            capturePhoto(context, imageCapture) { uri ->
                                viewModel.onImageCaptured(activeSlot, uri)
                                // Auto-advance to next empty slot
                                val nextEmpty = ImageSlot.values()
                                    .firstOrNull { it !in uiState.capturedImages && it != activeSlot }
                                if (nextEmpty != null) activeSlot = nextEmpty
                            }
                        }
                )

                // Submit button
                Button(
                    onClick  = {
                        viewModel.submitObservation(context, onSuccess = onObservationSubmitted)
                    },
                    modifier = Modifier
                        .height(52.dp)
                        .widthIn(min = 80.dp),
                    shape    = RoundedCornerShape(14.dp),
                    colors   = ButtonDefaults.buttonColors(
                        containerColor = Sapphire500,
                        contentColor   = Color.White
                    ),
                    enabled  = !uiState.isSubmitting && uiState.capturedImages.isNotEmpty()
                ) {
                    if (uiState.isSubmitting) {
                        CircularProgressIndicator(
                            modifier  = Modifier.size(18.dp),
                            color     = Color.White,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Text("Submit", fontWeight = FontWeight.SemiBold)
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text  = "${uiState.capturedImages.size}/4 images · tap a slot to target it",
                style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceMuted,
                textAlign = TextAlign.Center
            )
        }
    }
}

// ─── CameraX Photo Capture Helper ────────────────────────────────────────────

private fun capturePhoto(
    context: Context,
    imageCapture: ImageCapture?,
    onCaptured: (android.net.Uri) -> Unit
) {
    imageCapture ?: return

    val name = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(System.currentTimeMillis())
    val contentValues = ContentValues().apply {
        put(MediaStore.MediaColumns.DISPLAY_NAME, "LANDSENSE_$name")
        put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
        put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/LandSense")
    }
    val outputOptions = ImageCapture.OutputFileOptions.Builder(
        context.contentResolver,
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        contentValues
    ).build()

    imageCapture.takePicture(
        outputOptions,
        ContextCompat.getMainExecutor(context),
        object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                outputFileResults.savedUri?.let(onCaptured)
            }
            override fun onError(exception: ImageCaptureException) {
                // Silently log — never crash. UI shows slot as empty.
                exception.printStackTrace()
            }
        }
    )
}
