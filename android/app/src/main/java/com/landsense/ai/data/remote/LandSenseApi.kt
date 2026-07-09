package com.landsense.ai.data.remote

import com.landsense.ai.data.model.HeatmapPoint
import com.landsense.ai.data.model.HistoryEntry
import com.landsense.ai.data.model.ObservationRequest
import com.landsense.ai.data.model.ObservationResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

/**
 * LandSenseApi — Retrofit interface for all Backend endpoints.
 *
 * INTEGRATION RULES (must never be violated):
 * - Android talks ONLY to Backend.
 * - Do NOT add endpoints for AI, Cloud, Arduino, SQLite, or RERA directly.
 * - If the backend changes an endpoint, update ONLY this interface + matching models.
 * - The UI layer (ViewModels/Screens) must NEVER import Retrofit types directly.
 */
interface LandSenseApi {

    /**
     * Submit a site observation (images + GPS + optional voice).
     * Returns the fused Universal Data Object from the Backend pipeline.
     */
    @POST("observation")
    suspend fun submitObservation(
        @Body request: ObservationRequest
    ): Response<ObservationResponse>

    /**
     * Fetch heatmap data points for the Google Maps overlay.
     */
    @GET("heatmap")
    suspend fun getHeatmap(): Response<List<HeatmapPoint>>

    /**
     * Fetch the global observation history feed.
     */
    @GET("history")
    suspend fun getHistory(): Response<List<HistoryEntry>>
}
