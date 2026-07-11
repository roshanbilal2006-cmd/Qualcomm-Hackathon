package com.landsense.ai.presentation.splash

import androidx.lifecycle.ViewModel
import com.landsense.ai.data.repository.SettingsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class SplashViewModel @Inject constructor(
    private val settingsRepository: SettingsRepository
) : ViewModel() {
    fun isOnboardingComplete(): Boolean {
        return settingsRepository.isOnboardingComplete()
    }

    fun setOnboardingComplete(complete: Boolean) {
        settingsRepository.setOnboardingComplete(complete)
    }
}
