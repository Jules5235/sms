package nl.jules.naic.ui.detail

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Print
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import nl.jules.naic.R
import nl.jules.naic.ui.components.MetricRow
import nl.jules.naic.ui.components.PriceChart
import nl.jules.naic.ui.theme.adviceColor
import nl.jules.naic.ui.theme.adviceLabel
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DetailScreen(
    viewModel: DetailViewModel,
    onBack: () -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val instrument = uiState.instrument
    val score = uiState.naicScore
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(instrument?.ticker ?: "Detail")
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Terug")
                    }
                },
                actions = {
                    if (instrument != null && !uiState.isLoading && uiState.error == null) {
                        IconButton(
                            onClick = {
                                printFondsDetail(
                                    context = context,
                                    instrument = instrument,
                                    score = score,
                                    fundamentals = uiState.fundamentals,
                                    prices = uiState.prices,
                                )
                            },
                        ) {
                            Icon(
                                Icons.Filled.Print,
                                contentDescription = stringResource(R.string.print_page_content_description),
                            )
                        }
                    }
                },
            )
        },
    ) { padding ->
        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center,
                ) {
                    CircularProgressIndicator()
                }
            }

            uiState.error != null -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center,
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(stringResource(R.string.error_connection))
                        Text(
                            text = uiState.error ?: "",
                            color = MaterialTheme.colorScheme.error,
                        )
                        TextButton(onClick = { viewModel.load() }) {
                            Text(stringResource(R.string.retry))
                        }
                    }
                }
            }

            instrument != null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .verticalScroll(rememberScrollState())
                        .padding(16.dp),
                ) {
                    Text(
                        text = instrument.name ?: instrument.ticker,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                    )

                    score?.advice?.let { advice ->
                        Surface(
                            color = adviceColor(advice).copy(alpha = 0.15f),
                            shape = MaterialTheme.shapes.small,
                            modifier = Modifier.padding(vertical = 8.dp),
                        ) {
                            Text(
                                text = adviceLabel(advice),
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                                color = adviceColor(advice),
                                fontWeight = FontWeight.SemiBold,
                            )
                        }
                    }

                    instrument.indexCode?.let {
                        Text(
                            text = "Index: $it",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }

                    instrument.sector?.let {
                        Text(
                            text = "Sector: $it",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }

                    PriceChart(
                        prices = uiState.prices,
                        modifier = Modifier.padding(vertical = 16.dp),
                    )

                    if (score != null) {
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(
                                    text = stringResource(R.string.naic_title),
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.Bold,
                                )
                                score.winLossRatio?.let {
                                    MetricRow("Win/Loss ratio", fmt(it))
                                }
                                score.currentPrice?.let {
                                    MetricRow("Koers", "€ ${fmt(it)}")
                                }
                                score.buyThreshold?.let {
                                    MetricRow("Koopdrempel", "€ ${fmt(it)}")
                                }
                                score.holdThreshold?.let {
                                    MetricRow("Houd-drempel", "€ ${fmt(it)}")
                                }
                                score.totalReturn5yPct?.let {
                                    MetricRow("Rendement 5j", "${fmt(it)}%")
                                }
                                score.revenueCagr10y?.let {
                                    MetricRow("Omzet CAGR 10j", "${fmt(it)}%")
                                }
                                score.epsCagr10y?.let {
                                    MetricRow("EPS CAGR 10j", "${fmt(it)}%")
                                }
                                score.equityCagr10y?.let {
                                    MetricRow("EV CAGR 10j", "${fmt(it)}%")
                                }
                            }
                        }
                    }

                    if (uiState.fundamentals.isNotEmpty()) {
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 16.dp),
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(
                                    text = stringResource(R.string.fundamentals_title),
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.Bold,
                                )
                                uiState.fundamentals.take(5).forEach { f ->
                                    Text(
                                        text = "Jaar ${f.fiscalYear}",
                                        style = MaterialTheme.typography.titleSmall,
                                        modifier = Modifier.padding(top = 8.dp),
                                    )
                                    f.eps?.let { MetricRow("EPS", fmt(it)) }
                                    f.revenue?.let { MetricRow("Omzet", fmtLarge(it)) }
                                    f.netIncome?.let { MetricRow("Nettowinst", fmtLarge(it)) }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun fmt(value: Double): String = String.format(Locale.US, "%.2f", value)

private fun fmtLarge(value: Double): String = String.format(Locale.US, "%,.0f", value)
