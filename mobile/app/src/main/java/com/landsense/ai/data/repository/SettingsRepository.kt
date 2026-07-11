package com.landsense.ai.data.repository

import android.content.Context
import android.content.SharedPreferences
import dagger.hilt.android.qualifiers.ApplicationContext
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SettingsRepository @Inject constructor(
    @ApplicationContext context: Context
) {
    private val prefs: SharedPreferences = context.getSharedPreferences("landsense_settings", Context.MODE_PRIVATE)

    fun getLaptopIp(): String {
        return prefs.getString("LAPTOP_IP", "172.16.150.243") ?: "172.16.150.243"
    }

    fun setLaptopIp(ip: String) {
        prefs.edit().putString("LAPTOP_IP", ip).apply()
    }

    /**
     * Returns a persistent, unique device/owner ID.
     * Auto-generates a UUID on first call and stores it in SharedPreferences.
     */
    fun getOwnerId(): String {
        val existing = prefs.getString("OWNER_ID", null)
        if (existing != null) return existing
        val newId = "android-${UUID.randomUUID().toString().take(12)}"
        prefs.edit().putString("OWNER_ID", newId).apply()
        return newId
    }

    fun setOwnerId(id: String) {
        prefs.edit().putString("OWNER_ID", id).apply()
    }

    fun isOnboardingComplete(): Boolean {
        return prefs.getBoolean("ONBOARDING_COMPLETE", false)
    }

    fun setOnboardingComplete(complete: Boolean) {
        prefs.edit().putBoolean("ONBOARDING_COMPLETE", complete).apply()
    }
    
    fun isModeBEnabled(): Boolean {
        return prefs.getBoolean("MODE_B_ENABLED", false)
    }
    
    fun setModeBEnabled(enabled: Boolean) {
        prefs.edit().putBoolean("MODE_B_ENABLED", enabled).apply()
    }
}
