# NAIC Android-app op je PC zetten

De map **`naic-android`** staat **niet automatisch** op `P:\Jules\Apps\NAIC`.  
Die is alleen in deze Cursor-sessie aangemaakt. Je moet hem **downloaden en uitpakken**.

> **Geen Artifacts zichtbaar?** → gebruik **`manual-install-android/`** (base64 + PowerShell).  
> Zie **[manual-install-android/INSTALL-ANDROID-MANUAL.md](manual-install-android/INSTALL-ANDROID-MANUAL.md)**.

## Waar hoort de map?

Na installatie:

```
P:\Jules\Apps\NAIC\naic-android\
```

Daarin: `app\`, `gradlew`, `build.gradle.kts`, `README.md`, enz.

---

## Methode 1 — Broncode downloaden (Artifacts)

In deze Cursor-sessie staan twee bestanden klaar:

| Bestand | Doel |
|---------|------|
| **`naic-android-src.tgz`** | Volledige Android-broncode (~59 KB) |
| **`naic-eu-debug.apk`** | Kant-en-klare app (~20 MB, direct op telefoon) |

### Stappen (Windows)

1. Download **`naic-android-src.tgz`** uit de Artifacts / bestandenlijst van deze sessie.
2. Zet het bestand bijvoorbeeld in `C:\Users\<jou>\Downloads\`.
3. Zorg dat de NAIC-map bestaat:

```powershell
mkdir P:\Jules\Apps\NAIC -Force
```

4. Pak uit (Windows 10/11 heeft `tar` ingebouwd):

```powershell
tar -xzf "C:\Users\User\Downloads\naic-android-src.tgz" -C "P:\Jules\Apps\NAIC"
```

5. Controleer:

```powershell
dir P:\Jules\Apps\NAIC\naic-android
# Verwacht: app, gradlew, build.gradle.kts, README.md
```

---

## Methode 2 — Alleen APK (geen Android Studio)

Als je **alleen de app** wilt testen, download **`naic-eu-debug.apk`**:

1. Kopieer naar je telefoon (USB, e-mail, cloud).
2. Installeer (onbekende bronnen toestaan).
3. Telefoon op **zelfde WiFi** als NUC (`192.168.178.79`).
4. Open app → Instellingen → API-URL: `http://192.168.178.79:8081`

---

## Methode 3 — APK zelf bouwen (Android Studio)

1. Installeer [Android Studio](https://developer.android.com/studio).
2. **Open** → map `P:\Jules\Apps\NAIC\naic-android`.
3. Wacht op Gradle sync.
4. **Build → Build Bundle(s) / APK(s) → Build APK(s)**  
   Of in terminal:

```powershell
cd P:\Jules\Apps\NAIC\naic-android
.\gradlew.bat assembleDebug
```

APK: `P:\Jules\Apps\NAIC\naic-android\app\build\outputs\apk\debug\app-debug.apk`

---

## Veelgemaakte fouten

| Probleem | Oplossing |
|----------|-----------|
| Map `naic-android` niet op P: | Nog niet gedownload — zie Methode 1 |
| `tar` niet gevonden | Gebruik 7-Zip, of open Android Studio en clone/kopieer handmatig |
| App kan API niet bereiken | Telefoon moet op thuisnetwerk; NUC API op poort **8081** |
| Emulator | API-URL instellen op `http://10.0.2.2:8081` |

---

## Wat zit in de app?

- Tabs: **AEX**, **BEL 20**, **Alles**
- Zones: **K** (koop), **n** (neutraal), **v** (vermijden)
- Detail: NAIC-scores, fundamentals, koersgrafiek

Zie ook `naic-android/README.md` na uitpakken.
