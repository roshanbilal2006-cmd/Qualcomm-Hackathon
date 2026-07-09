package com.landsense.ai.data.network

import kotlinx.serialization.Serializable

@Serializable
data class ObservationRequest(
    val images: List<String>,
    val latitude: String,
    val longitude: String,
    val timestamp: String,
    val voice_query: String?,
    val device: String = "OnePlus15"
)

@Serializable
data class ObservationResponse(
    val construction_stage: String = "Unknown",
    val progress_percent: Int = 0,
    val confidence: Double = 0.0,
    val dust_level: String = "Unknown",
    val noise_level: String = "Unknown",
    val development_score: Int = 0,
    val nearby_projects: Int = 0,
    val summary: String = ""
)

@Serializable
data class HeatmapResponse(
    val points: List<HeatmapPoint> = emptyList()
)

@Serializable
data class HeatmapPoint(
    val latitude: Double,
    val longitude: Double,
    val activity_level: String // "High", "Medium", "Low"
)
