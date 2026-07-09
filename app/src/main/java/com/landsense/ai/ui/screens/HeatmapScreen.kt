package com.landsense.ai.ui.screens

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.GoogleMap
import com.google.maps.android.compose.Marker
import com.google.maps.android.compose.MarkerState
import com.google.maps.android.compose.rememberCameraPositionState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HeatmapScreen(
    onNavigateUp: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Community Heatmap") },
                navigationIcon = {
                    IconButton(onClick = onNavigateUp) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
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
            val singapore = LatLng(1.3521, 103.8198)
            val cameraPositionState = rememberCameraPositionState {
                position = CameraPosition.fromLatLngZoom(singapore, 11f)
            }
            
            GoogleMap(
                modifier = Modifier.fillMaxSize(),
                cameraPositionState = cameraPositionState
            ) {
                // Mock points for heatmap since actual heatmap tiles require more setup
                Marker(
                    state = MarkerState(position = LatLng(1.35, 103.82)),
                    title = "High Activity",
                    snippet = "Construction density: High"
                )
                Marker(
                    state = MarkerState(position = LatLng(1.36, 103.81)),
                    title = "Medium Activity",
                    snippet = "Construction density: Medium"
                )
            }
            
            // Map Overlay text
            Surface(
                modifier = Modifier.align(Alignment.TopCenter),
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.8f),
                shape = MaterialTheme.shapes.medium
            ) {
                Text(
                    text = "Showing Construction Density",
                    modifier = Modifier.padding(8.dp),
                    style = MaterialTheme.typography.labelMedium
                )
            }
        }
    }
}
