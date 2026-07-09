package com.landsense.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.landsense.ai.ui.navigation.NavGraph
import com.landsense.ai.ui.theme.LandSenseTheme

/**
 * MainActivity — single Activity host for the Jetpack Compose navigation graph.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            LandSenseTheme {
                NavGraph()
            }
        }
    }
}
