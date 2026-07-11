package com.landsense.ai.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface ObservationDao {
    @Query("SELECT * FROM observations WHERE ownerId = :ownerId ORDER BY timestamp DESC")
    suspend fun getHistory(ownerId: String): List<ObservationEntity>

    @Query("SELECT * FROM observations WHERE observationId = :id")
    suspend fun getObservationById(id: String): ObservationEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertObservation(observation: ObservationEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertObservations(observations: List<ObservationEntity>)
    
    @Query("UPDATE observations SET isSynced = 1 WHERE observationId = :id")
    suspend fun markAsSynced(id: String)
}
