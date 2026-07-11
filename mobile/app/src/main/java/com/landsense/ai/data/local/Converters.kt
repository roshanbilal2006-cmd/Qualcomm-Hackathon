package com.landsense.ai.data.local

import androidx.room.TypeConverter
import com.landsense.ai.data.network.ReraProject
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class Converters {
    @TypeConverter
    fun fromStringList(value: List<String>): String = Json.encodeToString(value)

    @TypeConverter
    fun toStringList(value: String): List<String> = try {
        Json.decodeFromString(value)
    } catch (e: Exception) {
        emptyList()
    }

    @TypeConverter
    fun fromReraProjectList(value: List<ReraProject>): String = Json.encodeToString(value)

    @TypeConverter
    fun toReraProjectList(value: String): List<ReraProject> = try {
        Json.decodeFromString(value)
    } catch (e: Exception) {
        emptyList()
    }

    @TypeConverter
    fun fromDoubleList(value: List<Double>): String = Json.encodeToString(value)

    @TypeConverter
    fun toDoubleList(value: String): List<Double> = try {
        Json.decodeFromString(value)
    } catch (e: Exception) {
        emptyList()
    }
}
