package com.landsense.ai.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.landsense.ai.data.network.ReraProject

@Entity(tableName = "observations")
data class ObservationEntity(
    @PrimaryKey val observationId: String,
    val ownerId: String,
    val timestamp: String,
    val latitude: Double,
    val longitude: Double,
    val images: List<String>,
    val voiceQuery: String?,
    val constructionStage: String?,
    val confidence: Double?,
    val progress: Double?,
    val noiseDb: Double?,
    val dustPm25: Double?,
    val dustPm10: Double?,
    val sensorStatus: String,
    val reraProjects: List<ReraProject>,
    val developmentScore: Double,
    val summary: String,
    val embedding: List<Double>,
    val isSynced: Boolean = true
)
