# Architectuur NAIC EU

## Overzicht

```
┌─────────────────────────────┐         SSH/deploy          ┌──────────────────────────────┐
│  Ontwikkel-PC (Windows)     │  ────────────────────────►  │  NUC6i5 (24/7)               │
│  P:\Jules\Apps\NAIC         │                             │  192.168.178.79              │
│                             │                             │                              │
│  • broncode                 │                             │  /home/jules/naic/           │
│  • config                   │                             │    ├── naic_eu/  (app)       │
│  • deploy-scripts           │                             │    ├── data/                 │
│  • optioneel: test-db       │         later: app ────────►│    │     └── naic_eu.db ◄──┤
│                             │         analyseert DB       │    └── logs/                 │
└─────────────────────────────┘                             │  • ETL (systemd, za 07:00)   │
                                                            └──────────────────────────────┘
```

| Rol | Locatie | Wat staat er |
|-----|---------|------------|
| **Ontwikkeling** | `P:\Jules\Apps\NAIC` | Python-code, config, deploy-scripts |
| **Productie** | NUC6i5 `/home/jules/naic` | App-runtime, **database**, logs, ETL |
| **Database** | `/home/jules/naic/data/naic_eu.db` | Alleen op NUC — niet op P: |

De NUC draait 24/7 en is altijd bereikbaar op `192.168.178.79` voor je analyse-app.

## Workflows

### Ontwikkelen (PC)

```powershell
cd P:\Jules\Apps\NAIC
python -m venv .venv
.venv\Scripts\activate
pip install -e .

# Optioneel: kleine lokale test (niet de productie-db!)
naic-etl --limit 3 --db data/test/naic_test.db
```

Draai **geen** volledige productie-ETL op je PC — die hoort op de NUC.

### Deploy code naar NUC

```bash
cd P:/Jules/Apps/NAIC/deploy
./deploy-remote.sh
```

Synct alleen **code** naar de NUC. De productiedatabase blijft intact.

### ETL op NUC (automatisch)

Systemd-timer: elke **zaterdag 07:00** — haalt koersen/fundamenten op en herberekent NAIC-scores.

Handmatig:

```bash
ssh jules@192.168.178.79 "systemctl start naic-etl.service"
```

## Database benaderen (voor toekomstige app)

De productiedatabase staat op de NUC. Mogelijke aanpakken voor je analyse-app:

### 1. SSH + SQLite (eenvoudigst, nu al mogelijk)

```bash
ssh jules@192.168.178.79 "sqlite3 /home/jules/naic/data/naic_eu.db 'SELECT * FROM v_naic_ranking LIMIT 10;'"
```

Vanuit Python op je PC:

```python
import subprocess, json
result = subprocess.run(
    ["ssh", "jules@192.168.178.79",
     "sqlite3 -json /home/jules/naic/data/naic_eu.db 'SELECT * FROM v_naic_ranking'"],
    capture_output=True, text=True,
)
rows = json.loads(result.stdout)
```

### 2. SSH-tunnel + lokale SQLite-client

```bash
# Database tijdelijk lokaal benaderbaar via tunnel
ssh -L 2222:127.0.0.1:22 jules@192.168.178.79
# App opent via sshfs of remote sqlite over ssh
```

### 3. Samba read-only share (NUC deelt data-map)

Export `/home/jules/naic/data/` read-only naar je netwerk — app opent `\\192.168.178.79\naic-data\naic_eu.db`.

### 4. REST API (aanbevolen voor app) ✅

FastAPI-service op NUC6i5, poort **8080**:

```
http://192.168.178.79:8080/api/ranking/AEX
http://192.168.178.79:8080/docs
```

Je analyse-app doet HTTP-requests — geen directe SQLite-toegang nodig. Zie `docs/API.md`.

## Paden samengevat

| | Windows (dev) | NUC6i5 (prod) |
|--|---------------|---------------|
| Code | `P:\Jules\Apps\NAIC` | `/home/jules/naic` |
| Database | *(niet)* | `/home/jules/naic/data/naic_eu.db` |
| Logs | *(niet)* | `/home/jules/naic/logs/` |
| IP | — | `192.168.178.79` |
