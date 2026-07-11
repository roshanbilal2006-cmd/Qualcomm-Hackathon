package com.landsense.ai.util

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.task.vision.classifier.ImageClassifier
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OnDeviceClassifier @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private var imageClassifier: ImageClassifier? = null
    private val modelName = "construction_model.tflite"

    init {
        setupClassifier()
    }

    private fun setupClassifier() {
        try {
            val options = ImageClassifier.ImageClassifierOptions.builder()
                .setMaxResults(1)
                .build()
            imageClassifier = ImageClassifier.createFromFileAndOptions(context, modelName, options)
        } catch (e: Exception) {
            Log.e("OnDeviceClassifier", "LiteRT model not found. Ensure $modelName is in the assets folder.", e)
            imageClassifier = null
        }
    }

    /**
     * Classifies the image locally.
     * Returns a construction stage if the model exists, otherwise returns a mock offline estimation.
     */
    fun classifyImage(bitmap: Bitmap): String {
        val classifier = imageClassifier ?: return "Mock Stage (LiteRT model missing)"
        
        return try {
            val tensorImage = TensorImage.fromBitmap(bitmap)
            val results = classifier.classify(tensorImage)
            
            if (results.isNotEmpty() && results[0].categories.isNotEmpty()) {
                val category = results[0].categories[0]
                "${category.label} (${(category.score * 100).toInt()}%)"
            } else {
                "Unknown Stage"
            }
        } catch (e: Exception) {
            Log.e("OnDeviceClassifier", "Inference failed", e)
            "Inference Error"
        }
    }
}
