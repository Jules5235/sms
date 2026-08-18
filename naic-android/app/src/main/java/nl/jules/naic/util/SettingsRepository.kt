package nl.jules.naic.util

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import nl.jules.naic.BuildConfig

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "naic_settings")

class SettingsRepository(private val context: Context) {
    private val apiBaseUrlKey = stringPreferencesKey("api_base_url")

    val apiBaseUrl: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[apiBaseUrlKey] ?: BuildConfig.DEFAULT_API_BASE_URL
    }

    suspend fun setApiBaseUrl(url: String) {
        context.dataStore.edit { prefs ->
            prefs[apiBaseUrlKey] = url.trim().removeSuffix("/")
        }
    }
}
