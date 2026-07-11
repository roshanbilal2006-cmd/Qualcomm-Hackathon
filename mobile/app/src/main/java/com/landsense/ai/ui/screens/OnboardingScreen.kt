package com.landsense.ai.ui.screens

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.landsense.ai.presentation.splash.SplashViewModel
import kotlinx.coroutines.launch

data class OnboardingPage(
    val title: String,
    val description: String,
    val icon: ImageVector
)

val onboardingPages = listOf(
    OnboardingPage(
        title = "Edge AI Inference",
        description = "Analyze construction sites instantly using on-device neural networks. No internet required.",
        icon = Icons.Default.Memory
    ),
    OnboardingPage(
        title = "Real-time Auditing",
        description = "Capture images and voice context to build accurate developmental reports.",
        icon = Icons.Default.CameraAlt
    ),
    OnboardingPage(
        title = "Community Heatmap",
        description = "View crowdsourced urban activity globally in a beautiful interactive heatmap.",
        icon = Icons.Default.Map
    )
)

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun OnboardingScreen(
    onFinishOnboarding: () -> Unit,
    viewModel: SplashViewModel = hiltViewModel()
) {
    val pagerState = rememberPagerState(pageCount = { onboardingPages.size })
    val scope = rememberCoroutineScope()

    Scaffold(
        bottomBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Indicators
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    repeat(onboardingPages.size) { iteration ->
                        val color = if (pagerState.currentPage == iteration) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant
                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(color)
                        )
                    }
                }

                // Next/Get Started Button
                Button(
                    onClick = {
                        if (pagerState.currentPage < onboardingPages.size - 1) {
                            scope.launch {
                                pagerState.animateScrollToPage(pagerState.currentPage + 1)
                            }
                        } else {
                            // Can't easily get SettingsRepository here without a ViewModel, 
                            // we'll just emit the event up and let caller handle it, or use the SplashViewModel.
                            onFinishOnboarding()
                        }
                    },
                    shape = MaterialTheme.shapes.medium
                ) {
                    Text(if (pagerState.currentPage == onboardingPages.size - 1) "Get Started" else "Next")
                }
            }
        }
    ) { padding ->
        HorizontalPager(
            state = pagerState,
            modifier = Modifier.fillMaxSize().padding(padding)
        ) { position ->
            val page = onboardingPages[position]
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Icon(
                    imageVector = page.icon,
                    contentDescription = null,
                    modifier = Modifier.size(120.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(48.dp))
                Text(
                    text = page.title,
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = page.description,
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
