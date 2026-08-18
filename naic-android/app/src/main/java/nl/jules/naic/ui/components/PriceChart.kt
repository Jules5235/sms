package nl.jules.naic.ui.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.patrykandpatrick.vico.compose.cartesian.CartesianChartHost
import com.patrykandpatrick.vico.compose.cartesian.axis.rememberBottomAxis
import com.patrykandpatrick.vico.compose.cartesian.axis.rememberStartAxis
import com.patrykandpatrick.vico.compose.cartesian.layer.rememberLineCartesianLayer
import com.patrykandpatrick.vico.compose.cartesian.rememberCartesianChart
import com.patrykandpatrick.vico.compose.cartesian.rememberVicoScrollState
import com.patrykandpatrick.vico.core.cartesian.data.CartesianChartModelProducer
import com.patrykandpatrick.vico.core.cartesian.data.lineSeries
import nl.jules.naic.remote.model.PricePoint

@Composable
fun PriceChart(
    prices: List<PricePoint>,
    modifier: Modifier = Modifier,
) {
    if (prices.isEmpty()) {
        Text(
            text = "Geen koersdata beschikbaar",
            style = MaterialTheme.typography.bodyMedium,
            modifier = modifier.padding(16.dp),
        )
        return
    }

    val closes = remember(prices) {
        prices.mapNotNull { it.adjClose ?: it.close }
    }

    if (closes.isEmpty()) return

    val modelProducer = remember { CartesianChartModelProducer() }
    LaunchedEffect(closes) {
        modelProducer.runTransaction {
            lineSeries { series(closes) }
        }
    }

    Card(modifier = modifier.fillMaxWidth()) {
        Text(
            text = "Koers (1 jaar)",
            style = MaterialTheme.typography.titleSmall,
            modifier = Modifier.padding(start = 16.dp, top = 12.dp),
        )
        CartesianChartHost(
            chart = rememberCartesianChart(
                rememberLineCartesianLayer(),
                startAxis = rememberStartAxis(),
                bottomAxis = rememberBottomAxis(),
            ),
            modelProducer = modelProducer,
            scrollState = rememberVicoScrollState(),
            modifier = Modifier
                .fillMaxWidth()
                .height(220.dp)
                .padding(8.dp),
        )
    }
}
