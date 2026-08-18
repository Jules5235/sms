# Lokaal werken — NAIC EU

## Het probleem met Cloud Agent

Een **Cursor Cloud Agent** draait op een **externe VM**, niet op je Windows-PC.  
Bestanden die daar worden gemaakt staan dus **niet automatisch** op `P:\Jules\Apps\NAIC`.

Dat is geen bug — zo werkt Cloud Agent. Voor dagelijks werk is **lokaal ontwikkelen** praktischer.

---

## Aanbevolen setup

```
P:\Jules\Apps\NAIC          ← broncode (jij werkt hier)
        │
        │  deploy-remote.sh
        ▼
192.168.178.79 (NUC)        ← database + API 24/7
        │
        │  http://192.168.178.79:8081
        ▼
Telefoon (naic-android APK) ← analyse-app
```

| Waar | Wat |
|------|-----|
| **P:\Jules\Apps\NAIC** | Alle broncode: Python, Android, deploy, config |
| **NUC** | Alleen productie: database, ETL, API |
| **Cloud Agent** | Optioneel — niet nodig voor dagelijks werk |

---

## Eenmalig: volledig pakket op P: zetten

### Stap 1 — Installer opslaan

Sla dit bestand op vanuit deze Cursor-sessie:

```
manual-install-complete/install-to-p-drive-all-in-one.ps1
```

Naar bijvoorbeeld:

```
P:\Jules\Apps\NAIC\install-to-p-drive-all-in-one.ps1
```

*(Of eerst in Downloads, daarna verplaatsen.)*

### Stap 2 — Uitvoeren

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& "P:\Jules\Apps\NAIC\install-to-p-drive-all-in-one.ps1"
```

Dit zet **alles** in `P:\Jules\Apps\NAIC`:

- `naic_eu/` — Python ETL + API
- `naic-android/` — Android-app
- `deploy/` — NUC-deploy scripts
- `config/`, `schema.sql`, docs

### Stap 3 — Python-omgeving

```powershell
cd P:\Jules\Apps\NAIC
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
naic-etl --help
```

### Stap 4 — Android (optioneel)

```powershell
cd P:\Jules\Apps\NAIC\naic-android
.\gradlew.bat assembleDebug
```

---

## Voortaan lokaal verder werken

### Open project in Cursor **op je PC**

1. Cursor Desktop → **File → Open Folder**
2. Kies **`P:\Jules\Apps\NAIC`**
3. Gebruik **Agent / Chat lokaal** (niet Cloud Agent)

Zo staan alle bestanden direct op je schijf — geen Artifacts, geen base64.

### Wanneer Cloud Agent?

Alleen als je bewust een taak op afstand wilt laten draaien.  
Daarna: wijzigingen terug naar P: via git, zip, of handmatig kopiëren.

---

## Git als sync (optioneel, aanbevolen)

Maak een **privé GitHub-repo** en koppel je P:-map:

```powershell
cd P:\Jules\Apps\NAIC
git init
git remote add origin https://github.com/JOUW-ACCOUNT/naic-eu.git
git add .
git commit -m "Initial local NAIC EU"
git push -u origin main
```

Voordelen:

- Cloud Agent kan pushen, jij pullt op P:
- Of jij pusht vanaf P:, Cloud Agent pullt
- Geen handmatige zip/base64 meer

---

## Deploy naar NUC (vanaf P:)

In **Git Bash** op je PC:

```bash
cd /p/Jules/Apps/NAIC/deploy
./deploy-remote.sh
```

API op NUC: **http://192.168.178.79:8081**

---

## Samenvatting

| Doel | Waar |
|------|------|
| Bestanden beheren | `P:\Jules\Apps\NAIC` + Cursor Desktop lokaal |
| Database + API 24/7 | NUC |
| Android APK bouwen | `P:\Jules\Apps\NAIC\naic-android` |
| Cloud Agent | Alleen incidenteel |

**Regel:** Ontwikkel op P:, deploy naar NUC, test app tegen NUC-API.
