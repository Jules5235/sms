package nl.jules.naic

import android.app.Application
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import nl.jules.naic.remote.api.NaicApiFactory
import nl.jules.naic.remote.repository.NaicRepository
import nl.jules.naic.util.SettingsRepository

class NaicApplication : Application() {
    lateinit var settingsRepository: SettingsRepository
        private set

    lateinit var repository: NaicRepository
        private set

    override fun onCreate() {
        super.onCreate()
        settingsRepository = SettingsRepository(this)
        val baseUrl = runBlocking { settingsRepository.apiBaseUrl.first() }
        repository = NaicRepository(NaicApiFactory.create(baseUrl))
    }

    suspend fun refreshApiClient() {
        val baseUrl = settingsRepository.apiBaseUrl.first()
        repository.updateApi(NaicApiFactory.create(baseUrl))
    }
}
