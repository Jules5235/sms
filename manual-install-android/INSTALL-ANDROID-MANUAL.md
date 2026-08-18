# NAIC Android — handmatige installatie (zonder Artifacts)

Als je **geen Artifacts-download** ziet in Cursor, gebruik dit pakket.

## Wat je nodig hebt

Kopieer de map **`manual-install-android`** naar je PC, bijvoorbeeld:

```
P:\Jules\Apps\NAIC\manual-install-android\
```

Inhoud:

| Bestand | Functie |
|---------|---------|
| `install-android-all-in-one.ps1` | **Aanbevolen** — één script, geen extra bestanden |
| `install-android.ps1` + `part1.b64` … `part4.b64` | Alternatief met losse parts |
| `INSTALL-ANDROID-MANUAL.md` | Deze handleiding |

---

## Methode A — Alles-in-één (aanbevolen)

1. Sla **`install-android-all-in-one.ps1`** op op je PC  
   (via Cursor: rechtsklik → Save / kopieer inhoud naar bestand).

2. Open **PowerShell** en voer uit:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& "P:\Jules\Apps\NAIC\manual-install-android\install-android-all-in-one.ps1"
```

3. Controleer:

```powershell
dir P:\Jules\Apps\NAIC\naic-android
```

---

## Methode B — Met part-bestanden

1. Zorg dat **`part1.b64` t/m `part4.b64`** in dezelfde map staan als `install-android.ps1`.
2. Bestanden moeten **`part1.b64`** heten (niet `.txt`).
3. Voer uit:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& "P:\Jules\Apps\NAIC\manual-install-android\install-android.ps1"
```

---

## APK op je telefoon

De broncode bevat **geen** kant-en-klare APK (20 MB — te groot voor base64 in chat).

**Optie 1 — Zelf bouwen (Windows + JDK):**

```powershell
cd P:\Jules\Apps\NAIC\naic-android
.\gradlew.bat assembleDebug
```

APK: `app\build\outputs\apk\debug\app-debug.apk`

**Optie 2 — Android Studio:**

1. Open map `P:\Jules\Apps\NAIC\naic-android`
2. Build → Build APK(s)

**Optie 3 — Telefoon op WiFi:**

- Installeer APK via USB/kabel
- API-URL in app: `http://192.168.178.79:8081`

---

## Veelgemaakte fouten

| Fout | Oplossing |
|------|-----------|
| `Base64 lengte … verwacht 79232` | Part-bestanden incompleet of `.txt` extensie |
| `SHA256 mismatch` | Bestand beschadigd — opnieuw kopiëren |
| `tar` niet gevonden | Windows 10/11 update, of installeer Android Studio |
| `gradlew` faalt | Installeer JDK 17 + Android SDK via Android Studio |

---

## Integriteit (controle)

- Base64 totaal: **79232** tekens
- SHA256 van `.tgz`: `29c0a89e90929bf6d0fdf1758a22a9a93aaf3edbec3eb062a5695c0900375c49`

Het install-script controleert dit automatisch.
