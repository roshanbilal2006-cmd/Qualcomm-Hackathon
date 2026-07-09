package com.landsense.ai.data.repository

import com.landsense.ai.data.model.HeatmapPoint
import com.landsense.ai.data.model.HistoryEntry
import com.landsense.ai.data.model.ObservationRequest
import com.landsense.ai.data.model.ObservationResponse
import com.landsense.ai.data.remote.NetworkModule

/**
 * ObservationRepository — Single source of truth for all Backend API calls.
 *
 * ViewModels MUST go through the repository; they must never use [NetworkModule.api] directly.
 * This layer is the correct place to add caching (Room) or error-transformation in the future.
 */
class ObservationRepository {

    private val api = NetworkModule.api

    /**
     * Submit a new site observation to the backend pipeline.
     * Returns [Result.success] with the fused [ObservationResponse] or [Result.failure] on error.
     */
    suspend fun submitObservation(request: ObservationRequest): Result<ObservationResponse> {
        return try {
            val response = api.submitObservation(request)
            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    Result.success(body)
                } else {
                    Result.failure(Exception("Empty response from backend."))
                }
            } else {
                Result.failure(
                    Exception("Backend error ${response.code()}: ${response.message()}")
                )
            }
        } catch (e: Exception) {
            Result.failure(Exception("Unable to connect to backend. ${e.localizedMessage}"))
        }
    }

    /**
     * Fetch heatmap data points for the Maps overlay.
     */
    suspend fun getHeatmap(): Result<List<HeatmapPoint>> {
        return try {
            val response = api.getHeatmap()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception("Heatmap fetch failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Unable to connect. ${e.localizedMessage}"))
        }
    }

    /**
     * Fetch the global observation history feed.
     */
    suspend fun getHistory(): Result<List<HistoryEntry>> {
        return try {
            val response = api.getHistory()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception("History fetch failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Unable to connect. ${e.localizedMessage}"))
        }
    }
}
