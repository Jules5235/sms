# NAIC EU ophalen via GitHub (geen Artifacts nodig)

Het volledige NAIC-pakket staat op GitHub in branch **`naic-eu-local`**.

## Windows — direct naar P:

```powershell
# Eerste keer (map mag leeg zijn of nog niet bestaan)
git clone -b naic-eu-local https://github.com/Jules5235/sms.git P:\Jules\Apps\NAIC
```

Daarna heb je alles:

- `naic_eu/` — Python ETL + API
- `naic-android/` — Android-app
- `deploy/` — NUC-deploy
- `manual-install-complete/` — PowerShell-installers (fallback)

## Python starten

```powershell
cd P:\Jules\Apps\NAIC
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

## Updates ophalen

```powershell
cd P:\Jules\Apps\NAIC
git pull
```

## Android APK bouwen

```powershell
cd P:\Jules\Apps\NAIC\naic-android
.\gradlew.bat assembleDebug
```

## Lokaal verder werken

Open **`P:\Jules\Apps\NAIC`** in **Cursor Desktop** (niet Cloud Agent).

Zie **[LOCAL-FIRST.md](LOCAL-FIRST.md)**.

## GitHub URL

https://github.com/Jules5235/sms/tree/naic-eu-local
