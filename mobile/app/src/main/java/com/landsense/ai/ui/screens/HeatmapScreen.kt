package com.landsense.ai.ui.screens

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Point
import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import com.landsense.ai.data.network.HeatmapPoint
import com.landsense.ai.presentation.heatmap.HeatmapViewModel
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Overlay

// ─── Colour logic matching the laptop web dashboard ───────────────────────────
// Web legend: Heavy Activity = red, Standard = orange, Completed = cyan
private val ColourHeavy   = Color(0xFFE53935) // red
private val ColourStandard = Color(0xFFFF9800) // orange
private val ColourCompleted = Color(0xFF26C6DA) // cyan

private fun pointColor(point: HeatmapPoint): Color = when {
    point.stage?.lowercase()?.contains("complet") == true -> ColourCompleted
    (point.developmentScore) >= 70 -> ColourHeavy
    else -> ColourStandard
}

// ─── OSMDroid circle overlay ──────────────────────────────────────────────────
private class CircleOverlay(
    private val geoPoint: GeoPoint,
    private val color: Int,
    private val radiusPx: Float = 36f
) : Overlay() {
    private val fillPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        this.color = (color and 0xFFFFFF) or 0x99000000.toInt()
    }
    private val strokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4f
        this.color = color
    }

    override fun draw(canvas: Canvas, mapView: MapView, shadow: Boolean) {
        if (shadow) return
        val screenPoint = Point()
        mapView.projection.toPixels(geoPoint, screenPoint)
        canvas.drawCircle(screenPoint.x.toFloat(), screenPoint.y.toFloat(), radiusPx, fillPaint)
        canvas.drawCircle(screenPoint.x.toFloat(), screenPoint.y.toFloat(), radiusPx, strokePaint)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HeatmapScreen(
    onNavigateUp: () -> Unit,
    viewModel: HeatmapViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()
    var showMapView by remember { mutableStateOf(true) }
    val context = LocalContext.current

    // Initialise OSMDroid configuration once
    LaunchedEffect(Unit) {
        Configuration.getInstance().load(context, context.getSharedPreferences("osmdroid", Context.MODE_PRIVATE))
        Configuration.getInstance().userAgentValue = "com.landsense.ai"
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Community Heatmap") },
                navigationIcon = {
                    IconButton(onClick = onNavigateUp) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showMapView = !showMapView }) {
                        Icon(
                            if (showMapView) Icons.Default.List else Icons.Default.Map,
                            contentDescription = "Toggle view"
                        )
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
                        Text("Fetching heatmap from backend...",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                state.errorMessage != null -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center).padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.WifiOff, null,
                            modifier = Modifier.size(48.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Backend Offline", style = MaterialTheme.typography.titleMedium)
                        Text(state.errorMessage!!, style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(16.dp))
                        OutlinedButton(onClick = { viewModel.loadHeatmap() }) { Text("Retry") }
                    }
                }
                state.points.isEmpty() -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center).padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.Map, null,
                            modifier = Modifier.size(48.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("No observations yet", style = MaterialTheme.typography.titleMedium)
                        Text("Submit scans to see them appear on the heatmap.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                showMapView -> OsmHeatmapMap(points = state.points)
                else -> HeatmapListView(points = state.points)
            }

            // Legend + count chip at the top — matches web dashboard
            if (!state.isLoading && state.points.isNotEmpty()) {
                Surface(
                    modifier = Modifier.align(Alignment.TopCenter).padding(8.dp),
                    color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
                    shape = MaterialTheme.shapes.medium,
                    tonalElevation = 4.dp
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        LegendDot(ColourHeavy, "Heavy Activity")
                        LegendDot(ColourStandard, "Standard")
                        LegendDot(ColourCompleted, "Completed")
                    }
                }
            }
        }
    }
}

@Composable
private fun LegendDot(color: Color, label: String) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
        Box(
            modifier = Modifier
                .size(10.dp)
                .background(color, MaterialTheme.shapes.small)
        )
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurface)
    }
}

@Composable
private fun OsmHeatmapMap(points: List<HeatmapPoint>) {
    val center = GeoPoint(points.first().latitude, points.first().longitude)

    AndroidView(
        factory = { ctx ->
            MapView(ctx).apply {
                setTileSource(TileSourceFactory.MAPNIK)     // same OSM tiles as web dashboard
                setMultiTouchControls(true)
                controller.setZoom(12.0)
                controller.setCenter(center)
                setBuiltInZoomControls(true)

                // Add circle overlay for each point
                points.forEach { pt ->
                    val geoPoint = GeoPoint(pt.latitude, pt.longitude)
                    val color = pointColor(pt).toArgb()

                    // Filled circle (same style as web dashboard)
                    overlays.add(CircleOverlay(geoPoint, color))

                    // Tap-friendly marker with info
                    val marker = Marker(this).apply {
                        position = geoPoint
                        setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
                        title = pt.stage ?: "Unknown Stage"
                        snippet = buildString {
                            append("Score: ${pt.developmentScore.toInt()}")
                            pt.noiseDb?.let { append(" | Noise: ${it.toInt()} dB") }
                            pt.dustPm25?.let { append(" | PM2.5: ${it.toInt()} µg/m³") }
                        }
                        icon = null  // invisible — circle overlay is the visual
                    }
                    overlays.add(marker)
                }
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}

@Composable
private fun HeatmapListView(points: List<HeatmapPoint>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 56.dp, bottom = 16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        item {
            Text("${points.size} Community Observations",
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(modifier = Modifier.height(4.dp))
        }
        items(points) { point ->
            val color = pointColor(point)
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
                        Text(point.stage ?: "Unknown Stage",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium)
                        Text("%.4f, %.4f".format(point.latitude, point.longitude),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                        point.noiseDb?.let {
                            Text("Noise: ${it.toInt()} dB",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                    Surface(
                        color = color.copy(alpha = 0.18f),
                        shape = MaterialTheme.shapes.small
                    ) {
                        Text(
                            "${point.developmentScore.toInt()}",
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = color
                        )
                    }
                }
            }
        }
    }
}
