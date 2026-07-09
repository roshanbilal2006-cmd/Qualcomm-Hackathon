package com.landsense.ai.ui.heatmap

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*
import com.landsense.ai.data.model.HeatmapPoint
import com.landsense.ai.ui.theme.*

/**
 * HeatmapScreen — Google Maps full-screen overlay of construction activity.
 *
 * Each [HeatmapPoint] from GET /heatmap is drawn as a semi-transparent circle:
 *  - Score > 75  → Red   (High)
 *  - Score 40–75 → Amber (Medium)
 *  - Score < 40  → Green (Low)
 */
@Composable
fun HeatmapScreen(
    viewModel: HeatmapViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    // Default camera centered on Bengaluru (demo default — live GPS in v2)
    val defaultLatLng   = LatLng(12.9716, 77.5946)
    val cameraPositionState = rememberCameraPositionState {
        position = CameraPosition.fromLatLngZoom(defaultLatLng, 13f)
    }

    Box(modifier = Modifier.fillMaxSize().background(Surface900)) {

        if (uiState.isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.align(Alignment.Center),
                color    = Sapphire500
            )
        } else if (uiState.error != null) {
            // Error state with retry
            Column(
                modifier            = Modifier.align(Alignment.Center).padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(Icons.Filled.Warning, null, tint = HeatHigh,
                    modifier = Modifier.size(40.dp))
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    uiState.error ?: "Unable to connect.",
                    style     = MaterialTheme.typography.bodyMedium,
                    color     = OnSurfaceMuted
                )
                Spacer(modifier = Modifier.height(16.dp))
                Button(
                    onClick = { viewModel.loadHeatmap() },
                    colors  = ButtonDefaults.buttonColors(containerColor = Sapphire500)
                ) {
                    Icon(Icons.Filled.Refresh, null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Retry")
                }
            }
        } else {
            // ─── Google Map ───────────────────────────────────────────────
            GoogleMap(
                modifier            = Modifier.fillMaxSize(),
                cameraPositionState = cameraPositionState,
                properties          = MapProperties(mapType = MapType.NORMAL),
                uiSettings          = MapUiSettings(
                    zoomControlsEnabled = true,
                    myLocationButtonEnabled = true
                )
            ) {
                uiState.points.forEach { point ->
                    val color = heatColor(point.score)
                    Circle(
                        center      = LatLng(point.latitude, point.longitude),
                        radius      = 80.0,          // ~80m radius per observation
                        fillColor   = color.copy(alpha = 0.35f),
                        strokeColor = color.copy(alpha = 0.7f),
                        strokeWidth = 2f
                    )
                }
            }

            // ─── Legend Overlay ───────────────────────────────────────────
            Surface(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(12.dp),
                shape = RoundedCornerShape(10.dp),
                color = Surface800.copy(alpha = 0.9f)
            ) {
                Column(modifier = Modifier.padding(10.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Legend", style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceMuted, fontWeight = FontWeight.SemiBold)
                    LegendItem(HeatHigh,   "High  (>75)")
                    LegendItem(HeatMedium, "Medium (40–75)")
                    LegendItem(HeatLow,    "Low   (<40)")
                }
            }

            // ─── Point Count Badge ────────────────────────────────────────
            Surface(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .padding(12.dp),
                shape = RoundedCornerShape(50.dp),
                color = Surface800.copy(alpha = 0.9f)
            ) {
                Text(
                    "${uiState.points.size} scans",
                    style    = MaterialTheme.typography.labelMedium,
                    color    = OnSurface,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }
        }
    }
}

@Composable
private fun LegendItem(color: Color, label: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Surface(
            modifier = Modifier.size(10.dp),
            shape    = androidx.compose.foundation.shape.CircleShape,
            color    = color
        ) {}
        Spacer(modifier = Modifier.width(6.dp))
        Text(label, style = MaterialTheme.typography.labelSmall, color = OnSurfaceMuted)
    }
}

private fun heatColor(score: Double): Color = when {
    score >= 75 -> HeatHigh
    score >= 40 -> HeatMedium
    else        -> HeatLow
}
