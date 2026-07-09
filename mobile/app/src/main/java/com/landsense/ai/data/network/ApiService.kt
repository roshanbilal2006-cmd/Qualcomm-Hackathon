package com.landsense.ai.data.network

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {
    @POST("observation")
    suspend fun submitObservation(@Body request: ObservationRequest): ObservationResponse

    @GET("heatmap")
    suspend fun getHeatmap(): HeatmapResponse
}
