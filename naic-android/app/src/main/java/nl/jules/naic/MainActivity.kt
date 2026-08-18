package nl.jules.naic

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import nl.jules.naic.ui.navigation.NaicNavHost
import nl.jules.naic.ui.theme.NaicTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = application as NaicApplication
        setContent {
            NaicTheme {
                NaicNavHost(application = app)
            }
        }
    }
}
