package com.landsense.ai.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.*
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.landsense.ai.ui.screens.*

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Capture : Screen("capture")
    object Heatmap : Screen("heatmap")
    object History : Screen("history")
    object Settings : Screen("settings")
    object Chat : Screen("chat")
    object Result : Screen("result/{observationId}") {
        fun createRoute(observationId: String) = "result/$observationId"
    }
}

@Composable
fun AppNavGraph() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Screen.Home.route) {

        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToCapture = { navController.navigate(Screen.Capture.route) },
                onNavigateToHistory = { navController.navigate(Screen.History.route) },
                onNavigateToHeatmap = { navController.navigate(Screen.Heatmap.route) },
                onNavigateToSettings = { navController.navigate(Screen.Settings.route) },
                onNavigateToChat = { navController.navigate(Screen.Chat.route) }
            )
        }

        composable(Screen.Capture.route) {
            CaptureScreen(
                onNavigateUp = { navController.popBackStack() },
                onCaptureComplete = { observationId ->
                    // Navigate to result, clearing the capture screen from back stack
                    navController.navigate(Screen.Result.createRoute(observationId)) {
                        popUpTo(Screen.Capture.route) { inclusive = true }
                    }
                }
            )
        }

        composable(
            route = Screen.Result.route,
            arguments = listOf(navArgument("observationId") { type = NavType.StringType })
        ) { backStackEntry ->
            val observationId = backStackEntry.arguments?.getString("observationId") ?: ""
            ResultScreen(
                observationId = observationId,
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.History.route) {
            HistoryScreen(
                onNavigateUp = { navController.popBackStack() },
                onOpenResult = { observationId ->
                    navController.navigate(Screen.Result.createRoute(observationId))
                }
            )
        }

        composable(Screen.Heatmap.route) {
            HeatmapScreen(onNavigateUp = { navController.popBackStack() })
        }

        composable(Screen.Settings.route) {
            SettingsScreen(onNavigateUp = { navController.popBackStack() })
        }

        composable(Screen.Chat.route) {
            ChatScreen(onNavigateUp = { navController.popBackStack() })
        }
    }
}
