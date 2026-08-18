package nl.jules.naic.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import nl.jules.naic.remote.model.AdviceZone
import nl.jules.naic.remote.model.RankingItem
import nl.jules.naic.ui.theme.adviceColor

@Composable
fun ZoneSection(
    zone: AdviceZone,
    items: List<RankingItem>,
    showIndexBadge: Boolean,
    onItemClick: (RankingItem) -> Unit,
    modifier: Modifier = Modifier,
) {
    if (items.isEmpty()) return

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            text = "${zone.label} — ${items.size}",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            color = adviceColor(zone.code),
            modifier = Modifier.padding(bottom = 4.dp),
        )
        items.forEach { item ->
            StockRow(
                item = item,
                showIndexBadge = showIndexBadge,
                onClick = { onItemClick(item) },
            )
        }
    }
}
