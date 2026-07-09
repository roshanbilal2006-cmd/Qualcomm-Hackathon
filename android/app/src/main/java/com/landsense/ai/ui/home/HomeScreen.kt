package com.landsense.ai.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Satellite
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.landsense.ai.ui.theme.*

/**
 * HomeScreen — Landing screen.
 *
 * Shows the LandSense brand, a brief tagline, and the primary CTA to begin
 * a site scan. Judges should understand the purpose within 5 seconds.
 */
@Composable
fun HomeScreen(
    onNavigateToCapture: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Surface900)
    ) {
        // Background gradient accent
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(300.dp)
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            Navy600.copy(alpha = 0.6f),
                            Color.Transparent
                        )
                    )
                )
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 24.dp),
            verticalArrangement   = Arrangement.Center,
            horizontalAlignment   = Alignment.CenterHorizontally
        ) {

            // ─── Logo Icon ────────────────────────────────────────────────
            Surface(
                modifier = Modifier.size(88.dp),
                shape    = RoundedCornerShape(24.dp),
                color    = Navy700
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector        = Icons.Filled.Satellite,
                        contentDescription = "LandSense logo",
                        tint               = Sapphire500,
                        modifier           = Modifier.size(48.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(28.dp))

            // ─── App Name ─────────────────────────────────────────────────
            Text(
                text       = "LandSense AI",
                style      = MaterialTheme.typography.headlineLarge,
                color      = OnSurface,
                fontWeight = FontWeight.Bold,
                textAlign  = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text      = "Construction Intelligence · Powered by Snapdragon",
                style     = MaterialTheme.typography.bodyMedium,
                color     = OnSurfaceMuted,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(56.dp))

            // ─── Primary CTA ──────────────────────────────────────────────
            Button(
                onClick  = onNavigateToCapture,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape  = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Sapphire500,
                    contentColor   = Color.White
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp)
            ) {
                Icon(
                    imageVector        = Icons.Filled.CameraAlt,
                    contentDescription = null,
                    modifier           = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(10.dp))
                Text(
                    text       = "Scan Construction Site",
                    style      = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Spacer(modifier = Modifier.height(40.dp))

            // ─── Feature Chips ────────────────────────────────────────────
            Row(
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                FeatureChip("📷  Vision AI")
                FeatureChip("📍  GPS")
                FeatureChip("🎙  Voice")
            }
        }

        // ─── Footer ───────────────────────────────────────────────────────
        Text(
            text      = "Qualcomm Snapdragon Multiverse Hackathon 2026",
            style     = MaterialTheme.typography.labelSmall,
            color     = OnSurfaceMuted.copy(alpha = 0.6f),
            textAlign = TextAlign.Center,
            modifier  = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 16.dp)
                .fillMaxWidth()
        )
    }
}

@Composable
private fun FeatureChip(label: String) {
    Surface(
        shape = RoundedCornerShape(50.dp),
        color = Surface700
    ) {
        Text(
            text     = label,
            style    = MaterialTheme.typography.labelMedium,
            color    = OnSurfaceMuted,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
        )
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF0D1117)
@Composable
fun HomeScreenPreview() {
    LandSenseTheme {
        HomeScreen(onNavigateToCapture = {})
    }
}
