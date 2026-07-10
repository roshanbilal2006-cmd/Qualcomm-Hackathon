package com.landsense.ai.data.repository

import com.landsense.ai.data.network.ApiService
import com.landsense.ai.data.network.HeatmapResponse
import com.landsense.ai.data.network.ObservationRequest
import com.landsense.ai.data.network.ObservationResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

interface ObservationRepository {
    suspend fun submitObservation(request: ObservationRequest): Result<ObservationResponse>
    suspend fun getHeatmap(): Result<HeatmapResponse>
}

@Singleton
class ObservationRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : ObservationRepository {
    override suspend fun submitObservation(request: ObservationRequest): Result<ObservationResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.submitObservation(request)
                Result.success(response)
            } catch (e: Exception) {
                // Return failure, specific message is handled by ViewModel (e.g. "Unable to connect.")
                Result.failure(e)
            }
        }
    }

    override suspend fun getHeatmap(): Result<HeatmapResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getHeatmap()
                Result.success(response)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}
