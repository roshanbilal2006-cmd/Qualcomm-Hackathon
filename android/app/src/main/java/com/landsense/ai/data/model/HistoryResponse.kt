package com.landsense.ai.data.model

import com.google.gson.annotations.SerializedName

/**
 * GET /history — A condensed history entry for the History Screen list.
 *
 * The full [ObservationResponse] is fetched when the user taps a history item.
 */
data class HistoryEntry(
    @SerializedName("observation_id")
    val observationId: String = "",

    @SerializedName("timestamp")
    val timestamp: String = "",

    @SerializedName("latitude")
    val latitude: Double = 0.0,

    @SerializedName("longitude")
    val longitude: Double = 0.0,

    @SerializedName("construction_stage")
    val constructionStage: String = "Unknown",

    @SerializedName("progress")
    val progress: Double = 0.0,

    @SerializedName("development_score")
    val developmentScore: Double = 0.0
)
