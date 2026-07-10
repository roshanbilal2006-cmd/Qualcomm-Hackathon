package com.landsense.ai.ui.screens

import android.Manifest
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import com.landsense.ai.presentation.capture.CaptureViewModel
import com.landsense.ai.ui.components.CameraPreview
import java.util.concurrent.Executor

@OptIn(ExperimentalPermissionsApi::class, ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    onNavigateUp: () -> Unit,
    onCaptureComplete: () -> Unit,
    viewModel: CaptureViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    val permissionsState = rememberMultiplePermissionsState(
        permissions = listOf(
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.RECORD_AUDIO
        )
    )

    LaunchedEffect(Unit) {
        if (!permissionsState.allPermissionsGranted) {
            permissionsState.launchMultiplePermissionRequest()
        }
    }

    LaunchedEffect(state.uploadSuccess) {
        if (state.uploadSuccess) {
            onCaptureComplete()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Capture Site") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background
                )
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            if (!permissionsState.allPermissionsGranted) {
                Column(
                    modifier = Modifier.align(Alignment.Center).padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("We need Camera and Location permissions to capture data.")
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(onClick = { permissionsState.launchMultiplePermissionRequest() }) {
                        Text("Grant Permissions")
                    }
                }
            } else {
                // Main Capture UI
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    
                    // Upload Mode Toggle (Mode A vs Mode B)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("LiteRT/VLM Edge Processing (Mode B)", style = MaterialTheme.typography.bodyMedium)
                            Text(if (state.isModeBEnabled) "Enabled" else "Disabled (Mode A)", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Switch(
                            checked = state.isModeBEnabled,
                            onCheckedChange = { viewModel.toggleModeB(it) }
                        )
                    }

                    // Camera Preview
                    val context = LocalContext.current
                    val imageCapture = remember { ImageCapture.Builder().build() }

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentAlignment = Alignment.Center
                    ) {
                        Surface(
                            modifier = Modifier.fillMaxSize(),
                            color = MaterialTheme.colorScheme.surfaceVariant,
                            shape = MaterialTheme.shapes.medium
                        ) {
                            CameraPreview(imageCapture = imageCapture)
                        }
                        
                        // Capture Button
                        Button(
                            onClick = {
                                // Simulate actual capture success for now (actual file IO requires more setup)
                                viewModel.addImage("mock_base64_image_data_${System.currentTimeMillis()}")
                            },
                            modifier = Modifier.align(Alignment.BottomCenter).padding(16.dp)
                        ) {
                            Text("Take Photo (${state.images.size}/4)")
                        }
                    }

                    // Optional Voice Query
                    OutlinedButton(
                        onClick = {
                            // In real app, trigger SpeechRecognizer intent
                            viewModel.setVoiceQuery("Simulated voice query transcript")
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Default.Mic, contentDescription = "Voice Input")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(if (state.voiceQuery == null) "Add Voice Query (Optional)" else "Voice Query Added")
                    }

                    // Submit Button
                    Button(
                        onClick = { viewModel.submitObservation() },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = state.images.isNotEmpty() && !state.isUploading
                    ) {
                        if (state.isUploading) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(24.dp),
                                    color = MaterialTheme.colorScheme.onPrimary
                                )
                                state.vlmProcessingStatus?.let { status ->
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(status, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onPrimary)
                                }
                            }
                        } else {
                            Icon(Icons.Default.Check, contentDescription = "Submit")
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Submit Observation")
                        }
                    }
                }
            }

            // Error Snackbar
            state.errorMessage?.let { error ->
                Snackbar(
                    modifier = Modifier.align(Alignment.BottomCenter).padding(16.dp),
                    action = {
                        TextButton(onClick = { viewModel.clearError() }) {
                            Text("Dismiss", color = MaterialTheme.colorScheme.inversePrimary)
                        }
                    }
                ) {
                    Text(error)
                }
            }
        }
    }
}
