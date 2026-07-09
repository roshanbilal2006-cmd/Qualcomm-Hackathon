package com.landsense.ai.data.model

import com.google.gson.annotations.SerializedName

/**
 * Universal Data Object — Response from POST /observation.
 *
 * Mirrors the OBSERVATION_SCHEMA.md exactly.
 * Fields sourced from AI, IoT, MCP, and Fusion Engine — all orchestrated by Backend.
 * Android reads but NEVER writes AI/IoT fields.
 */
data class ObservationResponse(
    @SerializedName("observation_id")
    val observationId: String = "",

    @SerializedName("timestamp")
    val timestamp: String = "",

    @SerializedName("latitude")
    val latitude: Double = 0.0,

    @SerializedName("longitude")
    val longitude: Double = 0.0,

    // ─── AI Inference Fields (from AI Service via Backend) ────────────────
    @SerializedName("construction_stage")
    val constructionStage: String = "Unknown",

    @SerializedName("confidence")
    val confidence: Double = 0.0,

    @SerializedName("progress")
    val progress: Double = 0.0,

    @SerializedName("summary")
    val summary: String = "",

    // ─── IoT Sensor Fields (from Arduino via Backend) ─────────────────────
    @SerializedName("noise_db")
    val noiseDb: Double = 0.0,

    @SerializedName("dust_pm25")
    val dustPm25: Double = 0.0,

    @SerializedName("dust_pm10")
    val dustPm10: Double = 0.0,

    @SerializedName("sensor_status")
    val sensorStatus: String = "disconnected",

    // ─── MCP / RERA Fields (from SQLite/MCP via Backend) ─────────────────
    @SerializedName("rera_projects")
    val reraProjects: List<ReraProject> = emptyList(),

    // ─── Fusion Engine Fields ─────────────────────────────────────────────
    @SerializedName("development_score")
    val developmentScore: Double = 0.0
)

/**
 * A single nearby RERA-registered project.
 */
data class ReraProject(
    @SerializedName("name")
    val name: String = "",

    @SerializedName("builder")
    val builder: String = "",

    @SerializedName("status")
    val status: String = "",

    @SerializedName("distance")
    val distance: Double = 0.0
)
