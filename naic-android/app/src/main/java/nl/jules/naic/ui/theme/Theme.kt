package nl.jules.naic.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val ZoneKoop = Color(0xFF2E7D32)
private val ZoneNeutraal = Color(0xFF757575)
private val ZoneVermijden = Color(0xFFC62828)

val AdviceKColor = ZoneKoop
val AdviceNColor = ZoneNeutraal
val AdviceVColor = ZoneVermijden

private val LightColors = lightColorScheme(
    primary = Color(0xFF1B5E20),
    secondary = Color(0xFF388E3C),
    tertiary = Color(0xFF00695C),
    background = Color(0xFFF5F5F5),
    surface = Color.White,
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF81C784),
    secondary = Color(0xFFA5D6A7),
    tertiary = Color(0xFF4DB6AC),
)

@Composable
fun NaicTheme(content: @Composable () -> Unit) {
    val darkTheme = isSystemInDarkTheme()
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        content = content,
    )
}

fun adviceColor(advice: String): Color = when (advice) {
    "K" -> AdviceKColor
    "n" -> AdviceNColor
    else -> AdviceVColor
}

fun adviceLabel(advice: String): String = when (advice) {
    "K" -> "Koop"
    "n" -> "Neutraal"
    else -> "Vermijden"
}
