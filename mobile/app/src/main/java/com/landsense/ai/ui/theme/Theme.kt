package com.landsense.ai.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Qualcomm Brand Colors & Sleek Dark Mode Palette
val QualcommRed = Color(0xFFE31937)
val SleekBackground = Color(0xFF0A0A0A)
val SleekSurface = Color(0xFF141414)
val SleekSurfaceVariant = Color(0xFF1E1E1E)
val LightBackground = Color(0xFFF8F9FA)

private val DarkColorScheme = darkColorScheme(
    primary = QualcommRed,
    onPrimary = Color.White,
    primaryContainer = Color(0xFF33090F), // Very dark red tint for chips
    onPrimaryContainer = Color(0xFFFFD9DF),
    secondary = Color(0xFF3253AC), // Qualcomm Blue
    onSecondary = Color.White,
    background = SleekBackground,
    onBackground = Color(0xFFF1F1F1),
    surface = SleekSurface,
    onSurface = Color(0xFFF1F1F1),
    surfaceVariant = SleekSurfaceVariant,
    onSurfaceVariant = Color(0xFFA0A0A0),
    surfaceTint = Color.Transparent // Disable M3 red tinting on elevated surfaces
)

private val LightColorScheme = lightColorScheme(
    primary = QualcommRed,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFFFD9DF),
    onPrimaryContainer = Color(0xFF33090F),
    secondary = Color(0xFF3253AC),
    onSecondary = Color.White,
    background = LightBackground,
    onBackground = Color(0xFF121212),
    surface = Color.White,
    onSurface = Color(0xFF121212),
    surfaceVariant = Color(0xFFE0E0E0),
    onSurfaceVariant = Color(0xFF424242),
    surfaceTint = Color.Transparent
)

@Composable
fun LandSenseAITheme(
    darkTheme: Boolean = true, // Force dark theme for that premium startup feel by default
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
