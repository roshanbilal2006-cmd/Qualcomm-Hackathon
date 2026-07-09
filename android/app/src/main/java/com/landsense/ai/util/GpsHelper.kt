package com.landsense.ai.util

import android.annotation.SuppressLint
import android.content.Context
import android.location.Location
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * GpsHelper — Wraps FusedLocationProviderClient in a clean suspend function.
 *
 * Permissions must be granted BEFORE calling [getCurrentLocation].
 * Use [PermissionHelper] in the Compose layer to handle permission UI.
 */
object GpsHelper {

    /**
     * Returns the current device location as a [Location] object.
     * Throws an exception if GPS is unavailable or times out.
     *
     * @param context Application or Activity context.
     */
    @SuppressLint("MissingPermission")
    suspend fun getCurrentLocation(context: Context): Location {
        val fusedClient = LocationServices.getFusedLocationProviderClient(context)

        return suspendCancellableCoroutine { continuation ->
            fusedClient.getCurrentLocation(
                Priority.PRIORITY_HIGH_ACCURACY,
                null
            ).addOnSuccessListener { location ->
                if (location != null) {
                    continuation.resume(location)
                } else {
                    continuation.resumeWithException(
                        Exception("GPS location unavailable. Please enable location services.")
                    )
                }
            }.addOnFailureListener { exception ->
                continuation.resumeWithException(
                    Exception("GPS error: ${exception.localizedMessage}")
                )
            }
        }
    }
}
