package com.landsense.ai

import android.app.Application

/**
 * LandSenseApp — Application entry point.
 *
 * Responsible for initialising the NetworkModule (Retrofit singleton)
 * so it is ready before any Activity or ViewModel needs it.
 */
class LandSenseApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // NetworkModule is an object (singleton) — no explicit init required.
        // Add future SDK initialisations here (e.g. Firebase, WorkManager).
    }
}
