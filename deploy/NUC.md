# NAIC op NUC6i5 — productie

| Item | Waarde |
|------|--------|
| Server | NUC6i5, Ubuntu 22.04 LTS |
| IP | **192.168.178.79** (24/7 bereikbaar) |
| Login | jules |
| App | `/home/jules/naic` |
| **Database** | `/home/jules/naic/data/naic_eu.db` |

Ontwikkel-broncode staat op je PC: `P:\Jules\Apps\NAIC`

## Eerste installatie

Vanaf je PC (Git Bash / WSL):

```bash
cd P:/Jules/Apps/NAIC/deploy
chmod +x deploy-remote.sh install.sh
./deploy-remote.sh
```

## Code-update (database blijft staan)

```bash
cd P:/Jules/Apps/NAIC/deploy
SKIP_ETL=1 ./deploy-remote.sh   # alleen code, geen ETL
# of met ETL:
./deploy-remote.sh
```

## Database benaderen (voor analyse-app)

```bash
# Ranking opvragen
ssh jules@192.168.178.79 "cd /home/jules/naic && .venv/bin/naic-ranking --index AEX"

# SQL direct
ssh jules@192.168.178.79 "sqlite3 /home/jules/naic/data/naic_eu.db 'SELECT COUNT(*) FROM naic_scores;'"
```

Zie `../ARCHITECTURE.md` voor opties om je app te koppelen.

## Onderhoud

```bash
ssh jules@192.168.178.79
systemctl list-timers naic-etl.timer      # volgende geplande ETL
systemctl start naic-etl.service          # handmatig bijwerken
tail -f /home/jules/naic/logs/etl-systemd.log
```
