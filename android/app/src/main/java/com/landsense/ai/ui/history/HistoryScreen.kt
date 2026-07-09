package com.landsense.ai.ui.history

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.landsense.ai.data.model.HistoryEntry
import com.landsense.ai.ui.theme.*
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter

/**
 * HistoryScreen — Scrollable list of past site scans.
 *
 * Each row shows: date, location coordinates, construction stage badge.
 * Tapping a row calls [onEntrySelected] for the caller to navigate.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    onEntrySelected: (HistoryEntry) -> Unit,
    viewModel: HistoryViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text("Scan History", style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.SemiBold)
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor    = Surface900,
                    titleContentColor = OnSurface
                ),
                actions = {
                    IconButton(onClick = { viewModel.loadHistory() }) {
                        Icon(Icons.Filled.Refresh, "Refresh", tint = OnSurfaceMuted)
                    }
                }
            )
        },
        containerColor = Surface900
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center),
                        color    = Sapphire500
                    )
                }
                uiState.error != null -> {
                    Column(
                        modifier            = Modifier.align(Alignment.Center).padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Filled.WifiOff, null, tint = HeatHigh,
                            modifier = Modifier.size(40.dp))
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(uiState.error ?: "Unable to connect.",
                            style = MaterialTheme.typography.bodyMedium, color = OnSurfaceMuted)
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { viewModel.loadHistory() },
                            colors  = ButtonDefaults.buttonColors(containerColor = Sapphire500)
                        ) {
                            Text("Retry")
                        }
                    }
                }
                uiState.entries.isEmpty() -> {
                    Column(
                        modifier            = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Filled.History, null, tint = OnSurfaceMuted,
                            modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("No scans yet.", style = MaterialTheme.typography.bodyMedium,
                            color = OnSurfaceMuted)
                    }
                }
                else -> {
                    LazyColumn(
                        modifier            = Modifier.fillMaxSize(),
                        contentPadding      = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        items(uiState.entries) { entry ->
                            HistoryEntryCard(entry = entry, onClick = { onEntrySelected(entry) })
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun HistoryEntryCard(entry: HistoryEntry, onClick: () -> Unit) {
    val stageColor = when (entry.constructionStage.lowercase()) {
        "completed"  -> HeatLow
        "structure"  -> Sapphire500
        "foundation" -> HeatMedium
        "excavation" -> HeatHigh
        else         -> OnSurfaceMuted
    }

    val formattedDate = remember(entry.timestamp) {
        try {
            val instant = Instant.parse(entry.timestamp)
            val formatter = DateTimeFormatter.ofPattern("dd MMM yyyy, HH:mm")
                .withZone(ZoneId.systemDefault())
            formatter.format(instant)
        } catch (e: Exception) {
            entry.timestamp
        }
    }

    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(14.dp),
        color = Surface800
    ) {
        Row(
            modifier          = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Stage color indicator bar
            Box(
                modifier = Modifier
                    .width(4.dp)
                    .height(56.dp)
                    .background(stageColor, RoundedCornerShape(50.dp))
            )

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Surface(
                        shape = RoundedCornerShape(6.dp),
                        color = stageColor.copy(alpha = 0.15f)
                    ) {
                        Text(
                            entry.constructionStage,
                            style     = MaterialTheme.typography.labelMedium,
                            color     = stageColor,
                            fontWeight = FontWeight.Medium,
                            modifier  = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                        )
                    }
                    Text(
                        "${entry.progress.toInt()}%",
                        style      = MaterialTheme.typography.labelMedium,
                        color      = OnSurfaceMuted,
                        fontWeight = FontWeight.Medium
                    )
                }
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    formattedDate,
                    style = MaterialTheme.typography.bodySmall,
                    color = OnSurface
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    "${String.format("%.4f", entry.latitude)}, ${String.format("%.4f", entry.longitude)}",
                    style = MaterialTheme.typography.labelSmall,
                    color = OnSurfaceMuted
                )
            }

            Spacer(modifier = Modifier.width(8.dp))
            Icon(
                Icons.Filled.ChevronRight, null,
                tint     = OnSurfaceMuted,
                modifier = Modifier.size(18.dp)
            )
        }
    }
}
