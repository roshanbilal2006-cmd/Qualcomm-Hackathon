package com.landsense.ai.data.model

import com.google.gson.annotations.SerializedName

/**
 * GET /heatmap — A single heatmap data point from the Cloud Layer.
 *
 * Each entry represents a coordinate with a construction activity score
 * used to render coloured overlays on Google Maps.
 */
data class HeatmapPoint(
    @SerializedName("latitude")
    val latitude: Double = 0.0,

    @SerializedName("longitude")
    val longitude: Double = 0.0,

    /**
     * Construction activity score 0–100.
     * > 75  → High   (red overlay)
     * 40–75 → Medium (yellow overlay)
     * < 40  → Low    (green overlay)
     */
    @SerializedName("score")
    val score: Double = 0.0,

    @SerializedName("construction_stage")
    val constructionStage: String = "",

    @SerializedName("observation_id")
    val observationId: String = ""
)
