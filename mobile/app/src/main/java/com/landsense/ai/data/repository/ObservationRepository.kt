package com.landsense.ai.data.repository

import com.landsense.ai.data.local.ObservationDao
import com.landsense.ai.data.local.ObservationEntity
import com.landsense.ai.data.network.ApiService
import com.landsense.ai.data.network.HeatmapPoint
import com.landsense.ai.data.network.HealthResponse
import com.landsense.ai.data.network.ObservationRequest
import com.landsense.ai.data.network.ObservationResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

// ─── Interface ────────────────────────────────────────────────────────────────
interface ObservationRepository {
    suspend fun submitObservation(request: ObservationRequest): Result<ObservationResponse>
    suspend fun saveLocalObservation(response: ObservationResponse, ownerId: String, isSynced: Boolean = false): Result<Unit>
    suspend fun getObservationById(id: String): Result<ObservationResponse>
    suspend fun getHistory(ownerId: String): Result<List<ObservationResponse>>
    suspend fun getHeatmap(): Result<List<HeatmapPoint>>
    suspend fun checkHealth(): Result<HealthResponse>
}

// ─── Implementation ───────────────────────────────────────────────────────────
@Singleton
class ObservationRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val observationDao: ObservationDao
) : ObservationRepository {

    override suspend fun submitObservation(request: ObservationRequest): Result<ObservationResponse> {
        return withContext(Dispatchers.IO) {
            runCatching {
                val response = apiService.submitObservation(request)
                // Save to Room on success
                observationDao.insertObservation(response.toEntity(request.ownerId ?: "unknown"))
                response
            }
        }
    }

    override suspend fun saveLocalObservation(response: ObservationResponse, ownerId: String, isSynced: Boolean): Result<Unit> {
        return withContext(Dispatchers.IO) {
            runCatching {
                observationDao.insertObservation(response.toEntity(ownerId, isSynced))
            }
        }
    }

    override suspend fun getObservationById(id: String): Result<ObservationResponse> {
        return withContext(Dispatchers.IO) {
            runCatching {
                try {
                    val response = apiService.getObservationById(id)
                    // We don't necessarily know the ownerId here, so we might skip inserting or query existing
                    response
                } catch (e: Exception) {
                    val cached = observationDao.getObservationById(id)
                    if (cached != null) {
                        cached.toResponse()
                    } else {
                        throw e
                    }
                }
            }
        }
    }

    override suspend fun getHistory(ownerId: String): Result<List<ObservationResponse>> {
        return withContext(Dispatchers.IO) {
            runCatching {
                try {
                    val remote = apiService.getHistory(ownerId)
                    // Cache the results
                    observationDao.insertObservations(remote.map { it.toEntity(ownerId) })
                    remote
                } catch (e: Exception) {
                    // Fallback to local
                    val local = observationDao.getHistory(ownerId)
                    if (local.isNotEmpty()) {
                        local.map { it.toResponse() }
                    } else {
                        throw e
                    }
                }
            }
        }
    }

    override suspend fun getHeatmap(): Result<List<HeatmapPoint>> {
        return withContext(Dispatchers.IO) {
            runCatching { apiService.getHeatmap() }
        }
    }

    override suspend fun checkHealth(): Result<HealthResponse> {
        return withContext(Dispatchers.IO) {
            runCatching { apiService.getHealth() }
        }
    }
}

// ─── Mappers ──────────────────────────────────────────────────────────────────

fun ObservationResponse.toEntity(ownerId: String, isSynced: Boolean = true): ObservationEntity {
    return ObservationEntity(
        observationId = this.observationId,
        ownerId = ownerId,
        timestamp = this.timestamp,
        latitude = this.latitude,
        longitude = this.longitude,
        images = this.images,
        voiceQuery = this.voiceQuery,
        constructionStage = this.constructionStage,
        confidence = this.confidence,
        progress = this.progress,
        noiseDb = this.noiseDb,
        dustPm25 = this.dustPm25,
        dustPm10 = this.dustPm10,
        sensorStatus = this.sensorStatus,
        reraProjects = this.reraProjects,
        developmentScore = this.developmentScore,
        summary = this.summary,
        embedding = this.embedding,
        isSynced = isSynced
    )
}

fun ObservationEntity.toResponse(): ObservationResponse {
    return ObservationResponse(
        observationId = this.observationId,
        timestamp = this.timestamp,
        latitude = this.latitude,
        longitude = this.longitude,
        images = this.images,
        voiceQuery = this.voiceQuery,
        constructionStage = this.constructionStage,
        confidence = this.confidence,
        progress = this.progress,
        noiseDb = this.noiseDb,
        dustPm25 = this.dustPm25,
        dustPm10 = this.dustPm10,
        sensorStatus = this.sensorStatus,
        reraProjects = this.reraProjects,
        developmentScore = this.developmentScore,
        summary = this.summary,
        embedding = this.embedding
    )
}
