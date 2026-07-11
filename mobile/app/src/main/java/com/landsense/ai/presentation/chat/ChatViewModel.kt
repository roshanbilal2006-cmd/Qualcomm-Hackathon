package com.landsense.ai.presentation.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.landsense.ai.data.network.ApiService
import com.landsense.ai.data.network.ChatRequest
import com.landsense.ai.util.LocationTracker
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ChatMessage(val role: String, val text: String)

data class ChatState(
    val messages: List<ChatMessage> = listOf(ChatMessage("assistant", "Hi! I am your LandSense AI assistant. Ask me anything about nearby construction.")),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val apiService: ApiService,
    private val locationTracker: LocationTracker
) : ViewModel() {

    private val _state = MutableStateFlow(ChatState())
    val state: StateFlow<ChatState> = _state.asStateFlow()

    fun sendMessage(text: String) {
        if (text.isBlank()) return

        // Add user message immediately
        _state.update { 
            it.copy(
                messages = it.messages + ChatMessage("user", text),
                isLoading = true,
                errorMessage = null
            )
        }

        viewModelScope.launch {
            try {
                // Get current location (fallback to 0,0 if disabled)
                val location = locationTracker.getCurrentLocation()
                val lat = location?.latitude ?: 0.0
                val lng = location?.longitude ?: 0.0

                val response = apiService.chat(ChatRequest(text, lat, lng))
                
                _state.update {
                    it.copy(
                        messages = it.messages + ChatMessage("assistant", response.answer),
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _state.update {
                    it.copy(
                        isLoading = false,
                        errorMessage = "Failed to connect: ${e.localizedMessage}"
                    )
                }
            }
        }
    }

    fun clearError() {
        _state.update { it.copy(errorMessage = null) }
    }
}
