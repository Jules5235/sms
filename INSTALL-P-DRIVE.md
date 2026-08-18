# Package naar P:\Jules\Apps\NAIC zetten

Stappen om de NAIC-package op je **P:-schijf** te zetten voor lokale ontwikkeling.

## Wat gaat waar?

| Locatie | Inhoud |
|---------|--------|
| `P:\Jules\Apps\NAIC` | Broncode (ontwikkeling) |
| NUC6i5 `/home/jules/naic` | Productie + database + API |

---

## Methode 1 — ZIP downloaden (aanbevolen op Windows)

De zip staat **niet automatisch** op je P:-schijf. Je moet het bestand eerst downloaden.

1. Download **`naic-eu-local.zip`** uit deze Cursor-sessie (Artifacts / bestandenlijst)
2. Zet het zip-bestand in een tijdelijke map, bijv. `C:\Users\User\Downloads\`
3. Maak de doelmap leeg/aan:

```powershell
mkdir P:\Jules\Apps\NAIC -Force
```

4. Pak uit met PowerShell (volledig pad naar het zip-bestand):

```powershell
Expand-Archive -Path "C:\Users\User\Downloads\naic-eu-local.zip" -DestinationPath "P:\Jules\Apps\NAIC" -Force
```

5. Controleer:

```powershell
dir P:\Jules\Apps\NAIC
# Verwacht: pyproject.toml, naic_eu\, deploy\, config\, schema.sql
```

> **Veelgemaakte fout:** `tar -xzf naic-eu-local.tar.gz` faalt als het zip/tar-bestand **niet in de huidige map staat**. Gebruik altijd het volledige pad, of kopieer het bestand eerst naar `P:\Jules\Apps\NAIC`.

---

## Methode 1b — Tarball (alternatief)

Als je `naic-eu-local.tar.gz` hebt gedownload naar `Downloads`:

```powershell
tar -xzf "C:\Users\User\Downloads\naic-eu-local.tar.gz" -C "P:\Jules\Apps\NAIC"
```

Of met 7-Zip: rechtsklik → Alles uitpakken naar `P:\Jules\Apps\NAIC`.

---

## Methode 2 — Handmatig kopiëren (USB / netwerkshare)

1. Kopieer de **hele map** `naic-eu` naar `P:\Jules\Apps\NAIC`
2. **Niet** kopiëren (optioneel overslaan):
   - `.venv/` — maak lokaal opnieuw aan
   - `data/*.db` — productiedata staat op NUC
   - `__pycache__/`, `*.egg-info/`

---

## Methode 3 — Git lokaal (zonder GitHub)

Als je de package als git-repo hebt (bijv. via USB):

```powershell
cd P:\Jules\Apps
git clone D:\backup\naic-eu NAIC
cd NAIC
```

Of kopieer de `.git`-map mee — er is **geen remote** naar GitHub.

---

## Na het kopiëren — setup op je PC

```powershell
cd P:\Jules\Apps\NAIC

# Python-omgeving
python -m venv .venv
.venv\Scripts\activate
pip install -e .

# Optionele lokale test (niet productie!)
naic-etl --limit 3 --db data\test\naic_test.db
```

---

## Deploy naar NUC6i5

Vanaf Git Bash of WSL op je PC:

```bash
cd /p/Jules/Apps/NAIC/deploy
chmod +x deploy-remote.sh install.sh
./deploy-remote.sh
```

Of in PowerShell met OpenSSH:

```powershell
cd P:\Jules\Apps\NAIC\deploy
bash deploy-remote.sh
```

---

## Eerste keer SSH naar NUC instellen

```powershell
# Test verbinding
ssh jules@192.168.178.79

# SSH-key (eenmalig, geen wachtwoord meer nodig)
ssh-keygen -t ed25519
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh jules@192.168.178.79 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

---

## REST API testen (na deploy)

In browser op je PC:

```
http://192.168.178.79:8080/health
http://192.168.178.79:8080/docs
http://192.168.178.79:8080/api/ranking/AEX
```

PowerShell:

```powershell
Invoke-RestMethod http://192.168.178.79:8080/api/ranking/AEX | ConvertTo-Json
```

---

## Checklist

- [ ] Map `P:\Jules\Apps\NAIC` bevat `pyproject.toml` en `naic_eu\`
- [ ] `.venv` aangemaakt en `pip install -e .` geslaagd
- [ ] SSH naar `jules@192.168.178.79` werkt
- [ ] `./deploy-remote.sh` uitgevoerd
- [ ] `http://192.168.178.79:8080/health` toont `"status": "ok"`
