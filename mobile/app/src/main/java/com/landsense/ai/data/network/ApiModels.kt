package com.landsense.ai.data.network

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// ─────────────────────────────────────────────
//  REQUEST — POST /observation
//  Images must be sent as "data:image/jpeg;base64,<data>" strings
//  1 to 4 images as per backend domain.py constraint
// ─────────────────────────────────────────────
@Serializable
data class ObservationRequest(
    val timestamp: String,
    @SerialName("owner_id") val ownerId: String? = null,
    val latitude: Double,
    val longitude: Double,
    val images: List<String>,          // "data:image/jpeg;base64,..." format
    @SerialName("voice_query") val voiceQuery: String? = null,
    @SerialName("noise_db") val noiseDb: Double? = null,
    @SerialName("dust_pm25") val dustPm25: Double? = null,
    @SerialName("dust_pm10") val dustPm10: Double? = null,
    @SerialName("sensor_timestamp") val sensorTimestamp: String? = null
)

// ─────────────────────────────────────────────
//  RESPONSE — POST /observation, GET /history, GET /observation/{id}
// ─────────────────────────────────────────────
@Serializable
data class ReraProject(
    val name: String,
    val builder: String,
    val status: String,
    val distance: Double
)

@Serializable
data class ObservationResponse(
    @SerialName("observation_id") val observationId: String,
    val timestamp: String,
    val latitude: Double,
    val longitude: Double,
    val images: List<String> = emptyList(),
    @SerialName("voice_query") val voiceQuery: String? = null,
    @SerialName("construction_stage") val constructionStage: String? = null,
    val confidence: Double? = null,
    val progress: Double? = null,
    @SerialName("noise_db") val noiseDb: Double? = null,
    @SerialName("dust_pm25") val dustPm25: Double? = null,
    @SerialName("dust_pm10") val dustPm10: Double? = null,
    @SerialName("sensor_status") val sensorStatus: String = "degraded",
    @SerialName("rera_projects") val reraProjects: List<ReraProject> = emptyList(),
    @SerialName("development_score") val developmentScore: Double = 0.0,
    val summary: String = "",
    val embedding: List<Double> = emptyList()
)

// ─────────────────────────────────────────────
//  HEATMAP — GET /heatmap
//  Backend serves this from cloud layer (port 8003), falls back to local SQLite
// ─────────────────────────────────────────────
@Serializable
data class HeatmapPoint(
    @SerialName("observation_id") val observationId: String = "",
    val latitude: Double,
    val longitude: Double,
    @SerialName("development_score") val developmentScore: Double = 0.0,
    @SerialName("noise_db") val noiseDb: Double? = null,
    @SerialName("dust_pm25") val dustPm25: Double? = null,
    val stage: String? = null
)

// ─────────────────────────────────────────────
//  HEALTH — GET /health
// ─────────────────────────────────────────────
@Serializable
data class HealthResponse(
    val status: String,
    val device: String = "",
    val role: String = ""
)

// ─────────────────────────────────────────────
//  CHAT — POST /chat
// ─────────────────────────────────────────────
@Serializable
data class ChatRequest(
    val question: String,
    val latitude: Double,
    val longitude: Double
)

@Serializable
data class ChatResponse(
    val answer: String
)
