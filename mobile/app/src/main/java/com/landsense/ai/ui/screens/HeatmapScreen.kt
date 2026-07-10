package com.landsense.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*
import com.landsense.ai.data.network.HeatmapPoint
import com.landsense.ai.presentation.heatmap.HeatmapViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HeatmapScreen(
    onNavigateUp: () -> Unit,
    viewModel: HeatmapViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()
    var showMapView by remember { mutableStateOf(true) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Community Heatmap") },
                navigationIcon = {
                    IconButton(onClick = onNavigateUp) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showMapView = !showMapView }) {
                        Icon(if (showMapView) Icons.Default.List else Icons.Default.Map, contentDescription = "Toggle view")
                    }
                    IconButton(onClick = { viewModel.loadHeatmap() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background)
            )
        }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding)) {
            when {
                state.isLoading -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Fetching heatmap from backend...", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                state.errorMessage != null -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center).padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.WifiOff, contentDescription = null, modifier = Modifier.size(48.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Backend Offline", style = MaterialTheme.typography.titleMedium)
                        Text(state.errorMessage!!, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(16.dp))
                        OutlinedButton(onClick = { viewModel.loadHeatmap() }) { Text("Retry") }
                    }
                }
                state.points.isEmpty() -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center).padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.MapOutlined, contentDescription = null, modifier = Modifier.size(48.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("No observations yet", style = MaterialTheme.typography.titleMedium)
                        Text("Submit scans to see them appear on the heatmap.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                showMapView -> HeatmapMapView(points = state.points)
                else -> HeatmapListView(points = state.points)
            }

            // Point count chip
            if (!state.isLoading && state.points.isNotEmpty()) {
                Surface(
                    modifier = Modifier.align(Alignment.TopCenter).padding(8.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.9f),
                    shape = MaterialTheme.shapes.medium
                ) {
                    Text(
                        "${state.points.size} observation${if (state.points.size != 1) "s" else ""} — tap icon to toggle view",
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
private fun HeatmapMapView(points: List<HeatmapPoint>) {
    val firstPoint = points.firstOrNull()
    val centerLat = firstPoint?.latitude ?: 12.9716
    val centerLng = firstPoint?.longitude ?: 77.7500

    val cameraPositionState = rememberCameraPositionState {
        position = CameraPosition.fromLatLngZoom(LatLng(centerLat, centerLng), 12f)
    }

    GoogleMap(
        modifier = Modifier.fillMaxSize(),
        cameraPositionState = cameraPositionState,
        properties = MapProperties(mapType = MapType.NORMAL),
        uiSettings = MapUiSettings(zoomControlsEnabled = true)
    ) {
        points.forEach { point ->
            val hue = scoreToHue(point.developmentScore)
            Marker(
                state = MarkerState(position = LatLng(point.latitude, point.longitude)),
                title = point.stage ?: "Unknown Stage",
                snippet = buildString {
                    append("Score: ${point.developmentScore.toInt()}")
                    point.noiseDb?.let { append(" | Noise: ${it.toInt()}dB") }
                    point.dustPm25?.let { append(" | PM2.5: ${it.toInt()}") }
                },
                icon = BitmapDescriptorFactory.defaultMarker(hue)
            )
        }
    }
}

@Composable
private fun HeatmapListView(points: List<HeatmapPoint>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        item {
            Text("${points.size} Community Observations", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(modifier = Modifier.height(4.dp))
        }
        items(points) { point ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp).fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(point.stage ?: "Unknown Stage", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
                        Text("%.4f, %.4f".format(point.latitude, point.longitude), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        point.noiseDb?.let { Text("Noise: ${it.toInt()} dB", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                    }
                    Surface(
                        color = scoreColor(point.developmentScore).copy(alpha = 0.2f),
                        shape = MaterialTheme.shapes.small
                    ) {
                        Text(
                            "${point.developmentScore.toInt()}",
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = scoreColor(point.developmentScore)
                        )
                    }
                }
            }
        }
    }
}

private fun scoreToHue(score: Double): Float {
    // Green (high score) → Yellow → Red (low score)
    return (score / 100.0 * 120.0).toFloat().coerceIn(0f, 120f)
}

@Composable
private fun scoreColor(score: Double): Color {
    return when {
        score >= 70 -> Color(0xFF4CAF50)
        score >= 40 -> Color(0xFFFF9800)
        else -> Color(0xFFF44336)
    }
}
