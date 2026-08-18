# NAIC EU — lokale package

NAIC/SSG-achtige analyse van **AEX** en **BEL 20** aandelen.

## Architectuur

| | Locatie |
|--|---------|
| **Ontwikkeling** (jij) | `P:\Jules\Apps\NAIC` — alleen broncode |
| **Productie** (24/7) | NUC6i5 `192.168.178.79` — database + ETL |
| **Database** | `/home/jules/naic/data/naic_eu.db` (alleen op NUC) |

Zie **[ARCHITECTURE.md](ARCHITECTURE.md)** voor het volledige plaatje en opties voor je analyse-app.

```
PC (P:\Jules\Apps\NAIC)  ──deploy──►  NUC6i5 (/home/jules/naic)
                                           └── data/naic_eu.db  ◄── jouw app later
```

## REST API (NUC6i5, 24/7)

Na deploy draait de API op je NUC:

| URL | Functie |
|-----|---------|
| http://192.168.178.79:8081/health | Status |
| http://192.168.178.79:8081/docs | Swagger UI |
| http://192.168.178.79:8081/api/ranking/AEX | AEX-ranking JSON |

Zie **[docs/API.md](docs/API.md)** voor alle endpoints.

## Android-app

Native analyse-app in **`naic-android/`** — tabs AEX / BEL 20 / Alles, zones K/n/v, detail + koersgrafiek.

```bash
cd naic-android
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
```

Zie **[naic-android/README.md](naic-android/README.md)** voor installatie op je telefoon.

## Package naar P: drive

Zie **[INSTALL-P-DRIVE.md](INSTALL-P-DRIVE.md)** voor kopie-instructies.

**Geen Artifacts?** Eén script voor alles (Python + Android + deploy):

→ **[manual-install-complete/install-to-p-drive-all-in-one.ps1](manual-install-complete/install-to-p-drive-all-in-one.ps1)**  
→ Handleiding: **[LOCAL-FIRST.md](LOCAL-FIRST.md)**

## Ontwikkelen op je PC

```powershell
cd P:\Jules\Apps\NAIC
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Optionele lokale test (niet productie):

```powershell
naic-etl --limit 3 --db data\test\naic_test.db
```

## Deploy naar NUC6i5

Synct **code** naar de NUC; de productiedatabase blijft staan.

```bash
cd P:/Jules/Apps/NAIC/deploy
./deploy-remote.sh
```

Eerste keer op NUC (via SSH):

```bash
ssh jules@192.168.178.79
# deploy-remote.sh doet dit automatisch, of handmatig:
bash /home/jules/naic/deploy/install.sh
```

## Database opvragen vanaf PC

```bash
ssh jules@192.168.178.79 "sqlite3 /home/jules/naic/data/naic_eu.db 'SELECT ticker, advice, win_loss_ratio FROM v_naic_ranking WHERE index_code=\"AEX\" LIMIT 10;'"
```

Of op de NUC:

```bash
ssh jules@192.168.178.79
cd /home/jules/naic && .venv/bin/naic-ranking --index AEX
```

## Commando's (op NUC)

| Commando | Functie |
|----------|---------|
| `naic-etl` | Volledige ETL + NAIC-scores |
| `naic-ranking --index AEX` | Ranking tonen |
| `systemctl start naic-etl.service` | Handmatig bijwerken |

ETL draait automatisch elke **zaterdag 07:00** (systemd-timer).

## Structuur (ontwikkel-PC)

```
P:\Jules\Apps\NAIC\
├── pyproject.toml
├── schema.sql
├── config/universes.yaml
├── naic_eu/              ← Python-pakket
├── deploy/
│   ├── nuc6i5.env        ← NUC-configuratie
│   ├── dev.env.example   ← PC-configuratie
│   └── deploy-remote.sh
└── data/test/            ← optioneel, lokale test-db
```

Productiedatabase staat **niet** op P: — alleen op de NUC.
