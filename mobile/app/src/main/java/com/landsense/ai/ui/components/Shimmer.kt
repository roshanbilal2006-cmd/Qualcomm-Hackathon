package com.landsense.ai.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

fun Modifier.shimmer(
    showShimmer: Boolean = true,
    shimmerColor: Color = Color.LightGray.copy(alpha = 0.4f),
    backgroundColor: Color = Color.LightGray.copy(alpha = 0.1f)
): Modifier = composed {
    if (!showShimmer) return@composed this

    val transition = rememberInfiniteTransition(label = "shimmer_transition")
    val translateAnim = transition.animateFloat(
        initialValue = -1000f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = 1200,
                easing = LinearEasing
            ),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_translate_anim"
    )

    val brush = Brush.linearGradient(
        colors = listOf(backgroundColor, shimmerColor, backgroundColor),
        start = Offset.Zero,
        end = Offset(x = translateAnim.value, y = translateAnim.value)
    )

    this.background(brush)
}
