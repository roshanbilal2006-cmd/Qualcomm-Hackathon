package com.landsense.ai.data.model

import com.google.gson.annotations.SerializedName

/**
 * POST /observation — Request body sent from Android to Backend.
 *
 * Matches the API contract exactly. Do NOT add extra fields.
 * If the backend changes its contract, update ONLY this file + LandSenseApi.kt.
 */
data class ObservationRequest(
    @SerializedName("images")
    val images: List<String>,           // Base64-encoded image strings

    @SerializedName("latitude")
    val latitude: Double,

    @SerializedName("longitude")
    val longitude: Double,

    @SerializedName("timestamp")
    val timestamp: String,              // ISO 8601 UTC e.g. "2026-07-08T09:40:00Z"

    @SerializedName("voice_query")
    val voiceQuery: String = "",        // Optional — empty string if not provided

    @SerializedName("device")
    val device: String = "OnePlus15"
)
