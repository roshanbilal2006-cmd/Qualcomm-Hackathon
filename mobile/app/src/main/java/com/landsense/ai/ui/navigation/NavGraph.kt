package com.landsense.ai.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.landsense.ai.ui.screens.CaptureScreen
import com.landsense.ai.ui.screens.HeatmapScreen
import com.landsense.ai.ui.screens.HistoryScreen
import com.landsense.ai.ui.screens.HomeScreen
import com.landsense.ai.ui.screens.ResultScreen
import com.landsense.ai.ui.screens.SettingsScreen

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Capture : Screen("capture")
    object Result : Screen("result")
    object History : Screen("history")
    object Heatmap : Screen("heatmap")
    object Settings : Screen("settings")
}

@Composable
fun LandSenseNavGraph(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route
    ) {
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToCapture = { navController.navigate(Screen.Capture.route) },
                onNavigateToHistory = { navController.navigate(Screen.History.route) },
                onNavigateToHeatmap = { navController.navigate(Screen.Heatmap.route) },
                onNavigateToSettings = { navController.navigate(Screen.Settings.route) }
            )
        }
        composable(Screen.Capture.route) {
            CaptureScreen(
                onNavigateUp = { navController.navigateUp() },
                onCaptureComplete = { navController.navigate(Screen.Result.route) {
                    popUpTo(Screen.Home.route)
                } }
            )
        }
        composable(Screen.Result.route) {
            ResultScreen(
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                }
            )
        }
        composable(Screen.History.route) {
            HistoryScreen(onNavigateUp = { navController.navigateUp() })
        }
        composable(Screen.Heatmap.route) {
            HeatmapScreen(onNavigateUp = { navController.navigateUp() })
        }
        composable(Screen.Settings.route) {
            SettingsScreen(onNavigateBack = { navController.navigateUp() })
        }
    }
}
