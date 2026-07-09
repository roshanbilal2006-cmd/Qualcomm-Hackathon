package com.landsense.ai.ui.theme

import androidx.compose.ui.graphics.Color

// ─── LandSense Brand Palette ─────────────────────────────────────────────────
// Primary — Deep Navy (professional, technical)
val Navy900 = Color(0xFF0A0E1A)
val Navy800 = Color(0xFF111827)
val Navy700 = Color(0xFF1A2540)
val Navy600 = Color(0xFF1E3A5F)

// Accent — Qualcomm Sapphire Blue
val Sapphire500 = Color(0xFF3A7BD5)
val Sapphire400 = Color(0xFF5B94E8)
val Sapphire300 = Color(0xFF82B1FF)

// Secondary Accent — Teal (data / sensor readings)
val Teal500 = Color(0xFF00BCD4)
val Teal400 = Color(0xFF26C6DA)
val Teal200 = Color(0xFF80DEEA)

// ─── Status Colours ───────────────────────────────────────────────────────────
// Construction Stage / Heatmap
val HeatHigh   = Color(0xFFE53935)   // Red   — High activity  (score > 75)
val HeatMedium = Color(0xFFFFB300)   // Amber — Medium activity (40–75)
val HeatLow    = Color(0xFF43A047)   // Green — Low activity   (< 40)

// Sensor / environmental
val DustColor  = Color(0xFFFF8F00)
val NoiseColor = Color(0xFFAB47BC)

// ─── Neutral Surface Colours ──────────────────────────────────────────────────
val Surface900  = Color(0xFF0D1117)
val Surface800  = Color(0xFF161B22)
val Surface700  = Color(0xFF21262D)
val Surface600  = Color(0xFF2D333B)
val OnSurface   = Color(0xFFE6EDF3)
val OnSurfaceMuted = Color(0xFF8B949E)

// ─── Score Gradient ───────────────────────────────────────────────────────────
val ScoreGradientStart = Sapphire500
val ScoreGradientEnd   = Teal500
