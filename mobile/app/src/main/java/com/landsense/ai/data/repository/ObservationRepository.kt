package com.landsense.ai.data.repository

import com.landsense.ai.data.network.ApiService
import com.landsense.ai.data.network.HeatmapPoint
import com.landsense.ai.data.network.HealthResponse
import com.landsense.ai.data.network.ObservationRequest
import com.landsense.ai.data.network.ObservationResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

interface ObservationRepository {
    suspend fun submitObservation(request: ObservationRequest): Result<ObservationResponse>
    suspend fun getObservationById(id: String): Result<ObservationResponse>
    suspend fun getHistory(ownerId: String? = null): Result<List<ObservationResponse>>
    suspend fun getHeatmap(): Result<List<HeatmapPoint>>
    suspend fun checkHealth(): Result<HealthResponse>
}

@Singleton
class ObservationRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : ObservationRepository {

    override suspend fun submitObservation(request: ObservationRequest): Result<ObservationResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Result.success(apiService.submitObservation(request))
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun getObservationById(id: String): Result<ObservationResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Result.success(apiService.getObservationById(id))
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun getHistory(ownerId: String?): Result<List<ObservationResponse>> {
        return withContext(Dispatchers.IO) {
            try {
                Result.success(apiService.getHistory(ownerId))
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun getHeatmap(): Result<List<HeatmapPoint>> {
        return withContext(Dispatchers.IO) {
            try {
                // Backend's /heatmap first tries cloud (port 8003), then falls back to local SQLite
                Result.success(apiService.getHeatmap())
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun checkHealth(): Result<HealthResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Result.success(apiService.getHealth())
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}
