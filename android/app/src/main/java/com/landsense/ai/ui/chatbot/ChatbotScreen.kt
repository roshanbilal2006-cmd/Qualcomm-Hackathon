package com.landsense.ai.ui.chatbot

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Construction
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.landsense.ai.ui.theme.*

/**
 * ChatbotScreen — Placeholder for the "Construction Assistant" feature.
 *
 * DESIGN DECISION: Navigation item is reserved and visible. Screen clearly
 * communicates the coming-soon state to judges without dead-ending them.
 * The UI scaffolding is ready for a chat message list + input to be added
 * when the LLM/MCP chatbot backend is integrated.
 */
@Composable
fun ChatbotScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Surface900),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier            = Modifier.padding(40.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Icon
            Surface(
                modifier = Modifier.size(96.dp),
                shape    = RoundedCornerShape(28.dp),
                color    = Navy700
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector        = Icons.Filled.Chat,
                        contentDescription = "Construction Assistant",
                        tint               = Sapphire500,
                        modifier           = Modifier.size(48.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(28.dp))

            Text(
                text       = "Construction Assistant",
                style      = MaterialTheme.typography.headlineSmall,
                color      = OnSurface,
                fontWeight = FontWeight.Bold,
                textAlign  = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text      = "Ask about construction stages, RERA compliance,\n" +
                            "environmental limits, and local regulations.",
                style     = MaterialTheme.typography.bodyMedium,
                color     = OnSurfaceMuted,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(32.dp))

            Surface(
                shape = RoundedCornerShape(10.dp),
                color = Sapphire500.copy(alpha = 0.1f),
                border = androidx.compose.foundation.BorderStroke(
                    1.dp, Sapphire500.copy(alpha = 0.3f)
                )
            ) {
                Text(
                    text     = "⚡  Coming Soon — Powered by Qualcomm AI",
                    style    = MaterialTheme.typography.labelMedium,
                    color    = Sapphire400,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF0D1117)
@Composable
fun ChatbotScreenPreview() {
    LandSenseTheme {
        ChatbotScreen()
    }
}
