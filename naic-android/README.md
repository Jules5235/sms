# NAIC EU — Android analyse-app

Native Android-app (APK) voor NAIC-ranking van **AEX** en **BEL 20**, gekoppeld aan de REST API op je NUC.

## Functies

- Tabs: **AEX**, **BEL 20**, **Alles**
- Aandelen gegroepeerd per zone: **K** (koop), **n** (neutraal), **v** (vermijden)
- Detailpagina met NAIC-scores, fundamentals en koersgrafiek (1 jaar)
- Instellingen: API-basis-URL (standaard `http://192.168.178.79:8081`)

## Vereisten

- Android Studio Ladybug (2024.2) of nieuwer
- JDK 17
- Telefoon op het **zelfde WiFi-netwerk** als de NUC
- NAIC API draait op de NUC (`naic-api.service`, poort **8081**)

## Project openen

1. Open Android Studio → **Open** → map `naic-android`
2. Wacht tot Gradle sync klaar is
3. Sluit telefoon aan via USB (USB-debugging aan) of start een emulator

> **Emulator:** gebruik `http://10.0.2.2:8081` als API-URL in Instellingen (host-forward naar je PC/NUC).

## APK bouwen

### Debug (snel testen)

```bash
cd naic-android
./gradlew assembleDebug
```

APK: `app/build/outputs/apk/debug/app-debug.apk`

### Release

```bash
./gradlew assembleRelease
```

## Installatie op telefoon

1. Kopieer `app-debug.apk` naar je telefoon
2. Sta installatie van onbekende bronnen toe
3. Open de app — controleer in **Instellingen** of de API-URL klopt
4. Zorg dat je telefoon op het thuisnetwerk zit (192.168.178.x)

## API-endpoints (gebruikt door de app)

| Endpoint | Gebruik |
|----------|---------|
| `GET /health` | Status + laatste score-datum |
| `GET /api/ranking/AEX` | AEX-ranking |
| `GET /api/ranking/BEL20` | BEL 20-ranking |
| `GET /api/instruments/{ticker}` | Detail + NAIC + fundamentals |
| `GET /api/instruments/{ticker}/prices?limit=365` | Koersgrafiek |

## Technologie

- Kotlin + Jetpack Compose
- Retrofit + Moshi
- Vico (grafieken)
- DataStore (API-URL opslaan)

## Structuur

```
app/src/main/java/nl/jules/naic/
├── remote/        API, modellen, repository
├── ui/            Schermen (home, detail, settings)
├── util/          Instellingen (DataStore)
└── MainActivity.kt
```
