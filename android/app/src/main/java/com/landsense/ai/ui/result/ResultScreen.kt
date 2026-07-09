package com.landsense.ai.ui.result

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.landsense.ai.data.model.ObservationResponse
import com.landsense.ai.data.model.ReraProject
import com.landsense.ai.ui.theme.*

/**
 * ResultScreen — Displays the fused construction report from the Backend.
 *
 * Layout:
 *  - Stage chip + progress bar
 *  - Confidence arc indicator
 *  - Development score (large number)
 *  - Environmental metrics (dust PM2.5, PM10, noise dB)
 *  - RERA nearby projects carousel
 *  - Summary text card
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultScreen(
    observation: ObservationResponse?,
    onNavigateBack: () -> Unit
) {
    val obs = observation ?: ObservationResponse(
        constructionStage = "Loading…",
        summary = "Report unavailable."
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Site Report",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.SemiBold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back",
                            tint = OnSurface)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Surface900,
                    titleContentColor = OnSurface
                )
            )
        },
        containerColor = Surface900
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {

            // ─── Stage + Progress ─────────────────────────────────────────
            StageProgressCard(
                stage    = obs.constructionStage,
                progress = obs.progress,
                confidence = obs.confidence
            )

            // ─── Development Score ────────────────────────────────────────
            DevelopmentScoreCard(score = obs.developmentScore)

            // ─── Environmental Metrics ────────────────────────────────────
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                MetricCard(
                    modifier  = Modifier.weight(1f),
                    label     = "PM2.5",
                    value     = "${obs.dustPm25}",
                    unit      = "µg/m³",
                    icon      = Icons.Filled.Cloud,
                    iconColor = DustColor
                )
                MetricCard(
                    modifier  = Modifier.weight(1f),
                    label     = "PM10",
                    value     = "${obs.dustPm10}",
                    unit      = "µg/m³",
                    icon      = Icons.Filled.Cloud,
                    iconColor = DustColor.copy(alpha = 0.7f)
                )
                MetricCard(
                    modifier  = Modifier.weight(1f),
                    label     = "Noise",
                    value     = "${obs.noiseDb}",
                    unit      = "dB",
                    icon      = Icons.Filled.GraphicEq,
                    iconColor = NoiseColor
                )
            }

            // ─── Sensor Status ────────────────────────────────────────────
            SensorStatusBadge(status = obs.sensorStatus)

            // ─── Nearby RERA Projects ─────────────────────────────────────
            if (obs.reraProjects.isNotEmpty()) {
                NearbyProjectsSection(projects = obs.reraProjects)
            }

            // ─── Summary ──────────────────────────────────────────────────
            SummaryCard(summary = obs.summary)

            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

// ─── Stage + Progress Card ────────────────────────────────────────────────────

@Composable
private fun StageProgressCard(stage: String, progress: Double, confidence: Double) {
    var animated by remember { mutableStateOf(false) }
    val animatedProgress by animateFloatAsState(
        targetValue = if (animated) (progress / 100f).toFloat() else 0f,
        animationSpec = tween(durationMillis = 1000),
        label = "progress"
    )
    LaunchedEffect(Unit) { animated = true }

    Surface(
        shape = RoundedCornerShape(16.dp),
        color = Surface800
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = Sapphire500.copy(alpha = 0.2f)
                ) {
                    Text(
                        text     = stage,
                        style    = MaterialTheme.typography.labelLarge,
                        color    = Sapphire400,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
                Text(
                    text  = "${progress.toInt()}%",
                    style = MaterialTheme.typography.headlineMedium,
                    color = OnSurface,
                    fontWeight = FontWeight.Bold
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            LinearProgressIndicator(
                progress          = { animatedProgress },
                modifier          = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(50.dp)),
                color             = Sapphire500,
                trackColor        = Surface700,
                strokeCap         = StrokeCap.Round
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text  = "Confidence: ${(confidence * 100).toInt()}%",
                style = MaterialTheme.typography.labelMedium,
                color = OnSurfaceMuted
            )
        }
    }
}

// ─── Development Score Card ───────────────────────────────────────────────────

@Composable
private fun DevelopmentScoreCard(score: Double) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = Surface800
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                contentAlignment = Alignment.Center,
                modifier         = Modifier.size(80.dp)
            ) {
                val scoreColor = when {
                    score >= 75 -> HeatLow
                    score >= 40 -> HeatMedium
                    else        -> HeatHigh
                }
                Text(
                    text       = score.toInt().toString(),
                    style      = MaterialTheme.typography.headlineLarge,
                    color      = scoreColor,
                    fontWeight = FontWeight.ExtraBold,
                    textAlign  = TextAlign.Center
                )
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(
                    "Development Score",
                    style      = MaterialTheme.typography.titleMedium,
                    color      = OnSurface,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(modifier = Modifier.height(4.dp))
                val label = when {
                    score >= 75 -> "High Activity · Compliant"
                    score >= 40 -> "Moderate Activity"
                    else        -> "Low Activity"
                }
                Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceMuted)
            }
        }
    }
}

// ─── Metric Card ──────────────────────────────────────────────────────────────

@Composable
private fun MetricCard(
    modifier: Modifier = Modifier,
    label: String,
    value: String,
    unit: String,
    icon: ImageVector,
    iconColor: Color
) {
    Surface(
        modifier = modifier,
        shape    = RoundedCornerShape(14.dp),
        color    = Surface800
    ) {
        Column(
            modifier            = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(icon, contentDescription = label, tint = iconColor,
                modifier = Modifier.size(18.dp))
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text       = value,
                style      = MaterialTheme.typography.titleMedium,
                color      = OnSurface,
                fontWeight = FontWeight.Bold
            )
            Text(unit,   style = MaterialTheme.typography.labelSmall, color = OnSurfaceMuted)
            Text(label,  style = MaterialTheme.typography.labelSmall, color = OnSurfaceMuted)
        }
    }
}

// ─── Sensor Status Badge ──────────────────────────────────────────────────────

@Composable
private fun SensorStatusBadge(status: String) {
    val (color, label) = when (status.lowercase()) {
        "connected"   -> HeatLow to "IoT Sensor: Connected"
        "degraded"    -> HeatMedium to "IoT Sensor: Degraded"
        else          -> HeatHigh to "IoT Sensor: Disconnected"
    }
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = color.copy(alpha = 0.12f),
        border = BorderStroke(1.dp, color.copy(alpha = 0.4f))
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier.size(8.dp).background(color, CircleShape)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(label, style = MaterialTheme.typography.labelMedium, color = color)
        }
    }
}

// ─── Nearby RERA Projects ─────────────────────────────────────────────────────

@Composable
private fun NearbyProjectsSection(projects: List<ReraProject>) {
    Column {
        Text(
            "Nearby RERA Projects",
            style      = MaterialTheme.typography.titleSmall,
            color      = OnSurface,
            fontWeight = FontWeight.SemiBold
        )
        Spacer(modifier = Modifier.height(8.dp))
        LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            items(projects) { project ->
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = Surface700,
                    modifier = Modifier.width(180.dp)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            project.name,
                            style = MaterialTheme.typography.labelLarge,
                            color = OnSurface,
                            fontWeight = FontWeight.Medium,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            project.builder,
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceMuted
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        val statusColor = when (project.status.lowercase()) {
                            "approved" -> HeatLow
                            "pending"  -> HeatMedium
                            else       -> HeatHigh
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(modifier = Modifier.size(6.dp)
                                .background(statusColor, CircleShape))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                project.status,
                                style = MaterialTheme.typography.labelSmall,
                                color = statusColor
                            )
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            "${project.distance.toInt()} m away",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceMuted
                        )
                    }
                }
            }
        }
    }
}

// ─── Summary Card ─────────────────────────────────────────────────────────────

@Composable
private fun SummaryCard(summary: String) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = Navy700
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Filled.AutoAwesome, null, tint = Sapphire500,
                    modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    "AI Summary",
                    style = MaterialTheme.typography.labelLarge,
                    color = Sapphire400,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text  = summary.ifBlank { "Summary not available for this observation." },
                style = MaterialTheme.typography.bodyMedium,
                color = OnSurface,
                lineHeight = 22.sp
            )
        }
    }
}
