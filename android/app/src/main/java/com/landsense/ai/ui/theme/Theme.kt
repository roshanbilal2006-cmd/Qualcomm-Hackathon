package com.landsense.ai.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

/**
 * LandSenseTheme — Always dark. Judges see the premium dark-mode interface.
 */
private val DarkColorScheme = darkColorScheme(
    primary          = Sapphire500,
    onPrimary        = OnSurface,
    primaryContainer = Navy600,
    onPrimaryContainer = Sapphire300,

    secondary        = Teal500,
    onSecondary      = Navy900,
    secondaryContainer = Navy700,
    onSecondaryContainer = Teal200,

    background       = Surface900,
    onBackground     = OnSurface,

    surface          = Surface800,
    onSurface        = OnSurface,

    surfaceVariant   = Surface700,
    onSurfaceVariant = OnSurfaceMuted,

    outline          = Surface600,
    outlineVariant   = Surface700,

    error            = HeatHigh,
    onError          = OnSurface
)

@Composable
fun LandSenseTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography  = LandSenseTypography,
        content     = content
    )
}
