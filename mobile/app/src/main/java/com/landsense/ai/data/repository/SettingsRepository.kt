package com.landsense.ai.data.repository

import android.content.Context
import android.content.SharedPreferences
import dagger.hilt.android.qualifiers.ApplicationContext
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
    
    fun isModeBEnabled(): Boolean {
        return prefs.getBoolean("MODE_B_ENABLED", false)
    }
    
    fun setModeBEnabled(enabled: Boolean) {
        prefs.edit().putBoolean("MODE_B_ENABLED", enabled).apply()
    }
}
