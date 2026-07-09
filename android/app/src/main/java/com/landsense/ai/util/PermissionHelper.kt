package com.landsense.ai.util

import android.Manifest
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState

/**
 * PermissionHelper — Composable wrappers for runtime permission handling.
 *
 * Note: This requires the Accompanist Permissions library OR the
 * androidx.activity:activity-compose permission APIs.
 *
 * The approach below uses ActivityResultContracts for maximum compatibility
 * without needing additional dependencies beyond what is already declared.
 */

/** All permissions the app requires up-front. */
val LANDSENSE_REQUIRED_PERMISSIONS = arrayOf(
    Manifest.permission.CAMERA,
    Manifest.permission.RECORD_AUDIO,
    Manifest.permission.ACCESS_FINE_LOCATION,
    Manifest.permission.ACCESS_COARSE_LOCATION
)
