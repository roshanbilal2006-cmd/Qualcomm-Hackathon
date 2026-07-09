package com.landsense.ai.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.PhotoCamera
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.landsense.ai.data.model.ObservationResponse
import com.landsense.ai.ui.chatbot.ChatbotScreen
import com.landsense.ai.ui.heatmap.HeatmapScreen
import com.landsense.ai.ui.history.HistoryScreen
import com.landsense.ai.ui.home.HomeScreen
import com.landsense.ai.ui.capture.CaptureScreen
import com.landsense.ai.ui.result.ResultScreen
import com.landsense.ai.ui.theme.Navy800
import com.landsense.ai.ui.theme.OnSurface
import com.landsense.ai.ui.theme.OnSurfaceMuted
import com.landsense.ai.ui.theme.Sapphire500

// ─── Route Constants ─────────────────────────────────────────────────────────
object Routes {
    const val HOME     = "home"
    const val CAPTURE  = "capture"
    const val RESULT   = "result"
    const val HEATMAP  = "heatmap"
    const val HISTORY  = "history"
    const val CHATBOT  = "chatbot"
}

// ─── Bottom Nav Items ─────────────────────────────────────────────────────────
private data class BottomNavItem(
    val route: String,
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)

private val bottomNavItems = listOf(
    BottomNavItem(Routes.HOME,    "Home",      Icons.Filled.Home),
    BottomNavItem(Routes.CAPTURE, "Scan",      Icons.Filled.PhotoCamera),
    BottomNavItem(Routes.HEATMAP, "Heatmap",   Icons.Filled.Map),
    BottomNavItem(Routes.HISTORY, "History",   Icons.Filled.History),
    BottomNavItem(Routes.CHATBOT, "Assistant", Icons.Filled.Chat)
)

/**
 * NavGraph — Root composable that owns navigation state.
 *
 * Result screen receives the observation response via the shared ViewModel
 * scoped to the nav back-stack entry.
 */
@Composable
fun NavGraph() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            val navBackStackEntry by navController.currentBackStackEntryAsState()
            val currentDestination = navBackStackEntry?.destination

            // Hide bottom bar on result screen to give full canvas to the report
            val hideOnRoutes = setOf(Routes.RESULT)
            val currentRoute = currentDestination?.route
            if (currentRoute !in hideOnRoutes) {
                NavigationBar(
                    containerColor = Navy800
                ) {
                    bottomNavItems.forEach { item ->
                        val selected = currentDestination?.hierarchy
                            ?.any { it.route == item.route } == true
                        NavigationBarItem(
                            selected = selected,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = {
                                Icon(
                                    imageVector = item.icon,
                                    contentDescription = item.label
                                )
                            },
                            label = { Text(item.label) },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor   = Sapphire500,
                                selectedTextColor   = Sapphire500,
                                unselectedIconColor = OnSurfaceMuted,
                                unselectedTextColor = OnSurfaceMuted,
                                indicatorColor      = Navy800
                            )
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController    = navController,
            startDestination = Routes.HOME,
            modifier         = Modifier.padding(innerPadding)
        ) {
            composable(Routes.HOME) {
                HomeScreen(onNavigateToCapture = { navController.navigate(Routes.CAPTURE) })
            }
            composable(Routes.CAPTURE) {
                CaptureScreen(
                    onObservationSubmitted = { response ->
                        // Pass the result to Result screen via the navigation back-stack
                        navController.currentBackStackEntry
                            ?.savedStateHandle
                            ?.set("observation", response)
                        navController.navigate(Routes.RESULT)
                    }
                )
            }
            composable(Routes.RESULT) {
                val observation = navController.previousBackStackEntry
                    ?.savedStateHandle
                    ?.get<ObservationResponse>("observation")
                ResultScreen(
                    observation  = observation,
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            composable(Routes.HEATMAP) {
                HeatmapScreen()
            }
            composable(Routes.HISTORY) {
                HistoryScreen(
                    onEntrySelected = { entry ->
                        // Future: navigate to detail with entry.observationId
                    }
                )
            }
            composable(Routes.CHATBOT) {
                ChatbotScreen()
            }
        }
    }
}
