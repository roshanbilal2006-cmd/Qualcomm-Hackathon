package com.landsense.ai.data.network

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    // POST /observation — submit a new scan
    @POST("observation")
    suspend fun submitObservation(@Body request: ObservationRequest): ObservationResponse

    // GET /observation/{id} — fetch a specific result
    @GET("observation/{id}")
    suspend fun getObservationById(@Path("id") id: String): ObservationResponse

    // GET /history?owner_id= — fetch scan history
    @GET("history")
    suspend fun getHistory(@Query("owner_id") ownerId: String? = null): List<ObservationResponse>

    // GET /heatmap — sourced from cloud layer (8003) or fallback to local SQLite
    @GET("heatmap")
    suspend fun getHeatmap(): List<HeatmapPoint>

    // GET /health — check if laptop backend is reachable
    @GET("health")
    suspend fun getHealth(): HealthResponse

    // GET /nearby — RERA projects near coordinates
    @GET("nearby")
    suspend fun getNearby(
        @Query("latitude") latitude: Double,
        @Query("longitude") longitude: Double,
        @Query("radius") radius: Double = 500.0
    ): List<HeatmapPoint>

    // POST /chat — AI Assistant
    @POST("chat")
    suspend fun chat(@Body request: ChatRequest): ChatResponse
}
