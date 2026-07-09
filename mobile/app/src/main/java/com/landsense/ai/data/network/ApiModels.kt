package com.landsense.ai.data.network

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class VisionData(
    val source: String,
    @SerialName("image_count") val imageCount: Int,
    val views: List<String>,
    @SerialName("construction_stage") val constructionStage: String,
    val progress: Double,
    val confidence: Double,
    val description: String,
    val embedding: List<Double>
)

@Serializable
data class ObservationRequest(
    val timestamp: String,
    @SerialName("owner_id") val ownerId: String,
    val latitude: Double,
    val longitude: Double,
    val images: List<String>, // Empty in Mode B, Populated in Mode A
    val vision: VisionData? = null, // Present in Mode B, null in Mode A
    @SerialName("voice_query") val voiceQuery: String? = null
)

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
    val images: List<String>,
    @SerialName("voice_query") val voiceQuery: String? = null,
    @SerialName("construction_stage") val constructionStage: String? = null,
    val confidence: Double? = null,
    val progress: Double? = null,
    @SerialName("noise_db") val noiseDb: Double? = null,
    @SerialName("dust_pm25") val dustPm25: Double? = null,
    @SerialName("dust_pm10") val dustPm10: Double? = null,
    @SerialName("sensor_status") val sensorStatus: String,
    @SerialName("rera_projects") val reraProjects: List<ReraProject>,
    @SerialName("development_score") val developmentScore: Double,
    val summary: String,
    val embedding: List<Double>
)

@Serializable
data class HeatmapPoint(
    @SerialName("observation_id") val observationId: String,
    val latitude: Double,
    val longitude: Double,
    @SerialName("development_score") val developmentScore: Double,
    @SerialName("noise_db") val noiseDb: Double? = null,
    @SerialName("dust_pm25") val dustPm25: Double? = null,
    val stage: String? = null
)
