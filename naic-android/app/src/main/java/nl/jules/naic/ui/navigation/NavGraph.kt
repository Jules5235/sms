package nl.jules.naic.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import nl.jules.naic.NaicApplication
import nl.jules.naic.remote.model.RankingItem
import nl.jules.naic.ui.detail.DetailScreen
import nl.jules.naic.ui.detail.DetailViewModel
import nl.jules.naic.ui.home.HomeScreen
import nl.jules.naic.ui.home.RankingViewModel
import nl.jules.naic.ui.settings.SettingsScreen

object Routes {
    const val HOME = "home"
    const val DETAIL = "detail/{ticker}"
    const val SETTINGS = "settings"

    fun detail(ticker: String) = "detail/$ticker"
}

@Composable
fun NaicNavHost(application: NaicApplication) {
    val navController = rememberNavController()
    val apiUrl by application.settingsRepository.apiBaseUrl.collectAsStateWithLifecycle(
        initialValue = nl.jules.naic.BuildConfig.DEFAULT_API_BASE_URL,
    )

    val rankingViewModel: RankingViewModel = viewModel(
        factory = RankingViewModelFactory(application.repository),
    )

    NavHost(navController = navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) {
            HomeScreen(
                viewModel = rankingViewModel,
                onStockClick = { item: RankingItem ->
                    navController.navigate(Routes.detail(item.ticker))
                },
                onSettingsClick = { navController.navigate(Routes.SETTINGS) },
            )
        }

        composable(
            route = Routes.DETAIL,
            arguments = listOf(navArgument("ticker") { type = NavType.StringType }),
        ) { backStackEntry ->
            val ticker = backStackEntry.arguments?.getString("ticker").orEmpty()
            val detailViewModel: DetailViewModel = viewModel(
                factory = DetailViewModelFactory(application.repository, ticker),
            )
            DetailScreen(
                viewModel = detailViewModel,
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.SETTINGS) {
            SettingsScreen(
                application = application,
                currentUrl = apiUrl,
                onBack = { navController.popBackStack() },
                onSaved = {
                    rankingViewModel.refresh()
                    navController.popBackStack()
                },
            )
        }
    }
}

class RankingViewModelFactory(
    private val repository: nl.jules.naic.remote.repository.NaicRepository,
) : androidx.lifecycle.ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(RankingViewModel::class.java)) {
            return RankingViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

class DetailViewModelFactory(
    private val repository: nl.jules.naic.remote.repository.NaicRepository,
    private val ticker: String,
) : androidx.lifecycle.ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(DetailViewModel::class.java)) {
            return DetailViewModel(repository, ticker) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
