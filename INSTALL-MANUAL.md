# Handmatige installatie (Optie C2) — zonder zip-download

Als je het zip-bestand niet kunt downloaden, volg deze stappen.

## Overzicht

1. Maak map `P:\Jules\Apps\NAIC\manual-install\`
2. Kopieer 4 base64-bestanden + 1 PowerShell-script (van Cursor-chat)
3. Voer `install-naic.ps1` uit
4. Installeer Python-omgeving

---

## Stap 1 — Mappen aanmaken

PowerShell:

```powershell
mkdir P:\Jules\Apps\NAIC\manual-install -Force
cd P:\Jules\Apps\NAIC\manual-install
```

---

## Stap 2 — Bestanden aanmaken

Maak in `manual-install\` deze **5 bestanden** met Kladblok (Notepad):

| Bestand | Inhoud |
|---------|--------|
| `part1.b64` | Kopieer uit chat: **DEEL 1/4** |
| `part2.b64` | Kopieer uit chat: **DEEL 2/4** |
| `part3.b64` | Kopieer uit chat: **DEEL 3/4** |
| `part4.b64` | Kopieer uit chat: **DEEL 4/4** |
| `install-naic.ps1` | Kopieer het korte install-script uit chat |

**Belangrijk bij .b64-bestanden:**
- Alleen de base64-tekst (geen aanhalingstekens, geen spaties aan begin/eind)
- Opslaan als **ANSI** of UTF-8 zonder BOM
- Geen regelafbrekingen midden in de tekst (alles op 1 regel per bestand)

---

## Stap 3 — Install-script uitvoeren

```powershell
cd P:\Jules\Apps\NAIC\manual-install
Set-ExecutionPolicy -Scope Process Bypass
.\install-naic.ps1
```

Controle:

```powershell
dir P:\Jules\Apps\NAIC
# Verwacht: pyproject.toml, naic_eu\, deploy\, config\
```

---

## Stap 4 — Python setup

```powershell
cd P:\Jules\Apps\NAIC
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Test (lokaal, klein):

```powershell
naic-etl --limit 2 --db data\test\naic_test.db
```

---

## Stap 5 — Deploy naar NUC6i5

Git Bash of WSL:

```bash
cd /p/Jules/Apps/NAIC/deploy
bash deploy-remote.sh
```

API test: http://192.168.178.79:8080/docs

---

## Alternatief: via NUC (minder kopiëren op PC)

1. SSH naar NUC: `ssh jules@192.168.178.79`
2. Plak het bootstrap-script uit `manual-install/bootstrap-nuc.sh` (in chat)
3. Op PC: `scp -r jules@192.168.178.79:/home/jules/naic/* P:/Jules/Apps/NAIC/`

Zie chat voor het bootstrap-script als je deze route preferereert.
