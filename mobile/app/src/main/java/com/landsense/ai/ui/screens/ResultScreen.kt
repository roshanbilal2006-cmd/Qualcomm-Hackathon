package com.landsense.ai.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.landsense.ai.data.network.ObservationResponse
import com.landsense.ai.data.network.ReraProject
import com.landsense.ai.presentation.result.ResultViewModel
import android.content.Context
import android.content.Intent
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Point
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.viewinterop.AndroidView
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Overlay
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultScreen(
    observationId: String,
    onNavigateHome: () -> Unit,
    viewModel: ResultViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        Configuration.getInstance().load(context, context.getSharedPreferences("osmdroid", Context.MODE_PRIVATE))
        Configuration.getInstance().userAgentValue = "com.landsense.ai"
    }

    LaunchedEffect(observationId) {
        viewModel.loadObservation(observationId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Analysis Report") },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background),
                actions = {
                    if (state.observation != null) {
                        IconButton(onClick = {
                            val obs = state.observation!!
                            val shareText = "LandSense AI Report\nStage: ${obs.constructionStage}\nScore: ${obs.developmentScore.toInt()}/100\nLocation: ${obs.latitude}, ${obs.longitude}\nSummary: ${obs.summary}"
                            val sendIntent = Intent(Intent.ACTION_SEND).apply {
                                putExtra(Intent.EXTRA_TEXT, shareText)
                                type = "text/plain"
                            }
                            context.startActivity(Intent.createChooser(sendIntent, "Share Report"))
                        }) {
                            Icon(Icons.Default.Share, contentDescription = "Share")
                        }
                    }
                }
            )
        },
        bottomBar = {
            Button(
                onClick = onNavigateHome,
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                enabled = !state.isLoading
            ) { Text("Back to Home") }
        }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding)) {
            when {
                state.isLoading -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Loading report from backend...", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                state.errorMessage != null -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center).padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.ErrorOutline, contentDescription = null, modifier = Modifier.size(48.dp), tint = MaterialTheme.colorScheme.error)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(state.errorMessage!!, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                state.observation != null -> {
                    ObservationReport(state.observation!!)
                }
            }
        }
    }
}

@Composable
private fun ObservationReport(obs: ObservationResponse) {
    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        contentPadding = PaddingValues(vertical = 16.dp)
    ) {
        // Stage + Confidence headline
        item {
            ReportCard(
                title = "Construction Stage",
                value = obs.constructionStage ?: "Unknown",
                subtitle = obs.progress?.let { "Progress: ${it.toInt()}%" },
                highlight = true
            )
        }

        // Animated Scores
        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                AnimatedScoreCard(
                    modifier = Modifier.weight(1f),
                    title = "AI Confidence",
                    score = obs.confidence?.let { it.toFloat() } ?: 0f,
                    valueText = obs.confidence?.let { "${(it * 100).toInt()}%" } ?: "—",
                    color = Color(0xFF4CAF50)
                )
                AnimatedScoreCard(
                    modifier = Modifier.weight(1f),
                    title = "Dev Score",
                    score = (obs.developmentScore / 100).toFloat(),
                    valueText = "${obs.developmentScore.toInt()}/100",
                    color = Color(0xFF3253AC)
                )
            }
        }

        // IoT Sensor data row
        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(modifier = Modifier.weight(1f)) {
                    ReportCard("Noise Level", obs.noiseDb?.let { "${it.toInt()} dB" } ?: "N/A")
                }
                Box(modifier = Modifier.weight(1f)) {
                    ReportCard("Dust PM2.5", obs.dustPm25?.let { "${it.toInt()} µg/m³" } ?: "N/A")
                }
            }
        }

        // Sensor status badge
        item {
            val isConnected = obs.sensorStatus == "connected"
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (isConnected) Color(0xFF0D2E0D) else Color(0xFF2E1A0D)
                ),
                border = androidx.compose.foundation.BorderStroke(
                    1.dp,
                    if (isConnected) Color(0xFF4CAF50) else Color(0xFFFF9800)
                )
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        if (isConnected) Icons.Default.Sensors else Icons.Default.SensorsOff,
                        contentDescription = null,
                        tint = if (isConnected) Color(0xFF4CAF50) else Color(0xFFFF9800)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        "IoT Sensor: ${if (isConnected) "Connected (Arduino UNO Q)" else "Degraded — no sensor in range"}",
                        style = MaterialTheme.typography.bodySmall,
                        color = if (isConnected) Color(0xFF4CAF50) else Color(0xFFFF9800)
                    )
                }
            }
        }

        // RERA Projects
        if (obs.reraProjects.isNotEmpty()) {
            item {
                ReraSection(obs.reraProjects)
            }
        }

        // Summary
        if (obs.summary.isNotEmpty()) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("AI Summary", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(obs.summary, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }

        // Observation metadata
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Observation Details", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Spacer(modifier = Modifier.height(4.dp))
                    MetaRow(Icons.Default.LocationOn, "GPS", "%.5f, %.5f".format(obs.latitude, obs.longitude))
                    MetaRow(Icons.Default.Schedule, "Time", obs.timestamp.take(19).replace("T", " "))
                    MetaRow(Icons.Default.Tag, "ID", obs.observationId.take(8) + "...")
                }
            }
        }

        // Mini Heatmap
        item {
            Card(
                modifier = Modifier.fillMaxWidth().height(200.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Box(modifier = Modifier.fillMaxSize()) {
                    MiniOsmMap(obs)
                }
            }
        }
    }
}

@Composable
private fun ReraSection(projects: List<ReraProject>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Business, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text("Nearby RERA Projects (${projects.size})", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(8.dp))
            projects.forEach { project ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(project.name, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
                        Text(project.builder, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Surface(
                            color = when (project.status.lowercase()) {
                                "approved" -> Color(0xFF0D2E0D)
                                "delayed" -> Color(0xFF2E2E0D)
                                else -> MaterialTheme.colorScheme.surfaceVariant
                            },
                            shape = MaterialTheme.shapes.small
                        ) {
                            Text(
                                project.status,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                style = MaterialTheme.typography.labelSmall,
                                color = when (project.status.lowercase()) {
                                    "approved" -> Color(0xFF4CAF50)
                                    "delayed" -> Color(0xFFFFEB3B)
                                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                                }
                            )
                        }
                        Text("${project.distance.toInt()}m away", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                if (project != projects.last()) Divider(color = MaterialTheme.colorScheme.surfaceVariant, thickness = 0.5.dp)
            }
        }
    }
}

@Composable
private fun MetaRow(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, value: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(14.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.width(6.dp))
        Text("$label: ", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
fun ReportCard(title: String, value: String, subtitle: String? = null, highlight: Boolean = false) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (highlight) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface
        ),
        border = androidx.compose.foundation.BorderStroke(
            1.dp,
            if (highlight) MaterialTheme.colorScheme.primary.copy(alpha = 0.5f) else MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                title,
                style = MaterialTheme.typography.labelMedium,
                color = if (highlight) MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f) else MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                value,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = if (highlight) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface
            )
            if (subtitle != null) {
                Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

@Composable
fun AnimatedScoreCard(modifier: Modifier = Modifier, title: String, score: Float, valueText: String, color: Color) {
    var startAnimation by remember { mutableStateOf(false) }
    val animatedScore by animateFloatAsState(
        targetValue = if (startAnimation) score else 0f,
        animationSpec = tween(durationMillis = 1500),
        label = "score_anim"
    )

    LaunchedEffect(Unit) {
        startAnimation = true
    }

    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(title, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(modifier = Modifier.height(16.dp))
            Box(contentAlignment = Alignment.Center, modifier = Modifier.size(72.dp)) {
                CircularProgressIndicator(
                    progress = { animatedScore },
                    color = color,
                    trackColor = color.copy(alpha = 0.15f),
                    strokeWidth = 6.dp,
                    strokeCap = StrokeCap.Round,
                    modifier = Modifier.fillMaxSize()
                )
                Text(valueText, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
        }
    }
}

private class MiniCircleOverlay(
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

@Composable
private fun MiniOsmMap(obs: ObservationResponse) {
    val geoPoint = GeoPoint(obs.latitude, obs.longitude)
    val color = when {
        obs.constructionStage?.lowercase()?.contains("complet") == true -> Color(0xFF26C6DA)
        obs.developmentScore >= 70 -> Color(0xFFE53935)
        else -> Color(0xFFFF9800)
    }.toArgb()

    AndroidView(
        factory = { ctx ->
            MapView(ctx).apply {
                setTileSource(TileSourceFactory.MAPNIK)
                setMultiTouchControls(false)
                controller.setZoom(16.0)
                controller.setCenter(geoPoint)
                overlays.add(MiniCircleOverlay(geoPoint, color))
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}
