package com.landsense.ai.util

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.content.Context
import android.util.Base64
import java.io.ByteArrayOutputStream
import java.io.InputStream

/**
 * ImageUtils — Bitmap ↔ Base64 conversion utilities for the observation payload.
 *
 * Images are encoded to Base64 JPEG before being included in the POST /observation body.
 * Quality is capped at 80 to balance payload size vs. AI inference accuracy.
 */
object ImageUtils {

    private const val JPEG_QUALITY = 80
    private const val MAX_DIMENSION = 1024   // Resize down to max 1024px on either axis

    /**
     * Converts a [Uri] (returned by CameraX ImageCapture) to a Base64-encoded JPEG string.
     */
    fun uriToBase64(context: Context, uri: Uri): String {
        val inputStream: InputStream = context.contentResolver.openInputStream(uri)
            ?: throw IllegalArgumentException("Cannot open URI: $uri")
        val bitmap = BitmapFactory.decodeStream(inputStream)
        return bitmapToBase64(bitmap)
    }

    /**
     * Converts a [Bitmap] to a Base64-encoded JPEG string.
     */
    fun bitmapToBase64(bitmap: Bitmap): String {
        val scaled = scaleBitmap(bitmap)
        val outputStream = ByteArrayOutputStream()
        scaled.compress(Bitmap.CompressFormat.JPEG, JPEG_QUALITY, outputStream)
        val byteArray = outputStream.toByteArray()
        return Base64.encodeToString(byteArray, Base64.NO_WRAP)
    }

    /**
     * Scales a bitmap so neither dimension exceeds [MAX_DIMENSION], preserving aspect ratio.
     */
    private fun scaleBitmap(bitmap: Bitmap): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        if (width <= MAX_DIMENSION && height <= MAX_DIMENSION) return bitmap
        val scale = MAX_DIMENSION.toFloat() / maxOf(width, height)
        val newWidth = (width * scale).toInt()
        val newHeight = (height * scale).toInt()
        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }
}
