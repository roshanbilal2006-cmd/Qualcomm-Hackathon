package com.landsense.ai.ui.screens

import android.Manifest
import androidx.camera.core.ImageCapture
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.AsyncImage
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import com.landsense.ai.presentation.capture.CaptureViewModel
import com.landsense.ai.ui.components.CameraPreview

@OptIn(ExperimentalPermissionsApi::class, ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    onNavigateUp: () -> Unit,
    onCaptureComplete: (String) -> Unit,  // passes observationId to ResultScreen
    viewModel: CaptureViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()
    val imageCapture = remember { ImageCapture.Builder().build() }

    val permissionsState = rememberMultiplePermissionsState(
        permissions = listOf(
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.RECORD_AUDIO
        )
    )

    LaunchedEffect(Unit) {
        if (!permissionsState.allPermissionsGranted) permissionsState.launchMultiplePermissionRequest()
    }

    LaunchedEffect(state.uploadSuccess, state.successObservationId) {
        if (state.uploadSuccess && state.successObservationId != null) {
            onCaptureComplete(state.successObservationId!!)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Capture Site") },
                navigationIcon = {
                    IconButton(onClick = onNavigateUp) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background)
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier.fillMaxSize().padding(padding)
        ) {
            if (!permissionsState.allPermissionsGranted) {
                PermissionRequest(onRequest = { permissionsState.launchMultiplePermissionRequest() })
            } else {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.spacedBy(0.dp)
                ) {
                    // Camera Preview
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f)
                            .clip(RoundedCornerShape(bottomStart = 16.dp, bottomEnd = 16.dp))
                    ) {
                        CameraPreview(imageCapture = imageCapture)

                        // Photo count badge
                        Surface(
                            modifier = Modifier.align(Alignment.TopEnd).padding(12.dp),
                            color = MaterialTheme.colorScheme.background.copy(alpha = 0.85f),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text(
                                text = "${state.images.size}/4 photos",
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }

                        // Shutter button
                        if (!state.isUploading) {
                            FloatingActionButton(
                                onClick = { viewModel.capturePhoto(imageCapture) },
                                modifier = Modifier.align(Alignment.BottomCenter).padding(24.dp),
                                containerColor = if (state.images.size >= 4) MaterialTheme.colorScheme.surfaceVariant else MaterialTheme.colorScheme.primary,
                                shape = CircleShape
                            ) {
                                Icon(
                                    if (state.isCapturing) Icons.Default.HourglassEmpty else Icons.Default.PhotoCamera,
                                    contentDescription = "Take Photo",
                                    modifier = Modifier.size(28.dp)
                                )
                            }
                        }
                    }

                    // Bottom panel
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        // Thumbnail strip
                        if (state.imageThumbnails.isNotEmpty()) {
                            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                itemsIndexed(state.imageThumbnails) { index, bytes ->
                                    Box {
                                        AsyncImage(
                                            model = bytes,
                                            contentDescription = "Photo ${index + 1}",
                                            modifier = Modifier
                                                .size(64.dp)
                                                .clip(RoundedCornerShape(8.dp))
                                                .border(1.dp, MaterialTheme.colorScheme.primary, RoundedCornerShape(8.dp)),
                                            contentScale = ContentScale.Crop
                                        )
                                        IconButton(
                                            onClick = { viewModel.removeImage(index) },
                                            modifier = Modifier
                                                .size(20.dp)
                                                .align(Alignment.TopEnd)
                                                .background(MaterialTheme.colorScheme.error, CircleShape)
                                        ) {
                                            Icon(Icons.Default.Close, contentDescription = "Remove", tint = Color.White, modifier = Modifier.size(12.dp))
                                        }
                                    }
                                }
                            }
                        }

                        // Voice query button
                        val speechLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
                            contract = androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult()
                        ) { result ->
                            viewModel.setRecording(false)
                            if (result.resultCode == android.app.Activity.RESULT_OK) {
                                val spokenText = result.data?.getStringArrayListExtra(android.speech.RecognizerIntent.EXTRA_RESULTS)?.get(0)
                                if (!spokenText.isNullOrEmpty()) {
                                    viewModel.setVoiceQuery(spokenText)
                                }
                            }
                        }

                        OutlinedButton(
                            onClick = {
                                if (state.voiceQuery != null) {
                                    viewModel.clearVoiceQuery()
                                } else {
                                    viewModel.setRecording(true)
                                    val intent = android.content.Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                                        putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                                        putExtra(android.speech.RecognizerIntent.EXTRA_PROMPT, "Describe the construction site...")
                                    }
                                    try {
                                        speechLauncher.launch(intent)
                                    } catch (e: Exception) {
                                        viewModel.setRecording(false)
                                        viewModel.setVoiceQuery("Speech recognition not available")
                                    }
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            if (state.isRecording) {
                                CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Listening...")
                            } else {
                                Icon(
                                    if (state.voiceQuery != null) Icons.Default.CheckCircle else Icons.Default.Mic,
                                    contentDescription = null,
                                    tint = if (state.voiceQuery != null) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = state.voiceQuery ?: "Add Voice Query (Optional)",
                                    maxLines = 1,
                                    overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
                                )
                            }
                        }

                        // Phase 11: Local AI prediction display
                        state.localPrediction?.let { prediction ->
                            Surface(
                                color = MaterialTheme.colorScheme.tertiaryContainer,
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Default.Memory, contentDescription = null, modifier = Modifier.size(16.dp), tint = MaterialTheme.colorScheme.onTertiaryContainer)
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("On-device AI: $prediction", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onTertiaryContainer)
                                }
                            }
                        }

                        // Submit button
                        Button(
                            onClick = { viewModel.submitObservation() },
                            modifier = Modifier.fillMaxWidth().height(52.dp),
                            enabled = state.images.isNotEmpty() && !state.isUploading,
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            if (state.isUploading) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(20.dp),
                                    color = MaterialTheme.colorScheme.onPrimary,
                                    strokeWidth = 2.dp
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Text(state.uploadStatusText ?: "Submitting...")
                            } else {
                                Icon(Icons.Default.CloudUpload, contentDescription = null)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Submit Observation (${state.images.size} photo${if (state.images.size != 1) "s" else ""})")
                            }
                        }
                    }
                }
            }

            // Error snackbar
            state.errorMessage?.let { error ->
                Snackbar(
                    modifier = Modifier.align(Alignment.BottomCenter).padding(16.dp),
                    action = {
                        TextButton(onClick = { viewModel.clearError() }) {
                            Text("Dismiss", color = MaterialTheme.colorScheme.inversePrimary)
                        }
                    }
                ) { Text(error) }
            }
        }
    }
}

@Composable
private fun PermissionRequest(onRequest: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(Icons.Default.CameraAlt, contentDescription = null, modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.primary)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Camera & Location Required", style = MaterialTheme.typography.titleLarge)
        Spacer(modifier = Modifier.height(8.dp))
        Text("LandSense AI needs camera to capture site photos and GPS to tag observations.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(24.dp))
        Button(onClick = onRequest, modifier = Modifier.fillMaxWidth()) { Text("Grant Permissions") }
    }
}
