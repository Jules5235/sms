# NAIC-database op NUC6i5 (TPCtoss.nl patroon)

Deployment naar **NUC6i5** — Ubuntu 22.04 LTS op `192.168.178.79`, login `jules`.

## Padstructuur (zelfde als TPCtoss)

| Omgeving | Pad |
|----------|-----|
| Windows | `P:\Jules\Apps\NAIC` |
| Ubuntu (NUC6i5) | `/mnt/p/Jules/Apps/NAIC` |

```
/mnt/p/Jules/Apps/NAIC/          ← P:/Jules/Apps/NAIC
├── run_etl.py
├── query_ranking.py
├── schema.sql
├── config/universes.yaml
├── naic_db/                     ← Python-pakket
├── deploy/
│   └── nuc6i5.env               ← omgevingsconfig
├── .venv/                       ← Python virtual environment
├── data/
│   └── naic_eu.db               ← SQLite-database
└── logs/
    ├── etl-YYYYMMDD-HHMMSS.log
    └── etl-systemd.log
```

## Optie A — Deploy vanaf je laptop (aanbevolen)

Op je Windows-PC (met SSH-toegang tot de NUC):

```bash
# Eenmalig: SSH-key instellen (als nog niet gedaan)
ssh-copy-id jules@192.168.178.79

# Clone repo (eenmalig)
git clone --branch cursor/eu-naic-database-poc-d9c0 https://github.com/Jules5235/sms.git
cd sms/naic_db/deploy

# Deploy naar NUC6i5
chmod +x deploy-remote.sh install.sh
./deploy-remote.sh
```

## Optie B — Direct op de NUC6i5

SSH naar de NUC:

```bash
ssh jules@192.168.178.79
```

Controleer eerst of P:-schijf gemount is:

```bash
mountpoint /mnt/p && ls /mnt/p/Jules/Apps/
```

Installatie:

```bash
curl -fsSL https://raw.githubusercontent.com/Jules5235/sms/cursor/eu-naic-database-poc-d9c0/naic_db/deploy/install.sh -o /tmp/naic-install.sh
chmod +x /tmp/naic-install.sh
sudo /tmp/naic-install.sh   # of zonder sudo als /mnt/p schrijfbaar is voor jules
```

> Het install-script verwacht dat `/mnt/p` de P:-schijf is. Als TPCtoss al draait, is deze mount waarschijnlijk al correct ingesteld.

## P:-schijf mount (indien nog niet aanwezig)

Als `/mnt/p` nog niet bestaat, voeg toe aan `/etc/fstab` (zelfde als TPCtoss):

```bash
sudo mkdir -p /mnt/p
# Voorbeeld — pas aan naar jouw NAS/share:
# //192.168.178.x/share /mnt/p cifs credentials=/home/jules/.smbcredentials,uid=jules,gid=jules,iocharset=utf8 0 0
sudo mount -a
```

Vraag: controleer op de NUC waar TPCtoss staat:

```bash
ls -la /mnt/p/Jules/Apps/
```

## Controle na installatie

Op de NUC:

```bash
cd /mnt/p/Jules/Apps/NAIC

# Ranking bekijken
NAIC_DB_PATH=/mnt/p/Jules/Apps/NAIC/data/naic_eu.db \
  .venv/bin/python query_ranking.py --index AEX

# Record-telling
sqlite3 data/naic_eu.db "
  SELECT 'instrumenten', COUNT(*) FROM instruments
  UNION ALL SELECT 'koersen', COUNT(*) FROM price_daily
  UNION ALL SELECT 'naic_scores', COUNT(*) FROM naic_scores;
"
# Verwacht: 45 / ~120000 / 45
```

Vanaf je laptop:

```bash
ssh jules@192.168.178.79 "sqlite3 /mnt/p/Jules/Apps/NAIC/data/naic_eu.db 'SELECT ticker, advice FROM v_naic_ranking WHERE index_code=\"AEX\" LIMIT 5;'"
```

## Automatische updates

Systemd-timer (zaterdag 07:00):

```bash
systemctl list-timers naic-etl.timer
systemctl start naic-etl.service          # handmatig nu draaien
tail -f /mnt/p/Jules/Apps/NAIC/logs/etl-systemd.log
```

## Configuratie aanpassen

Bestand: `/mnt/p/Jules/Apps/NAIC/deploy/nuc6i5.env`

```bash
NUC_HOST=192.168.178.79
NUC_USER=jules
APP_DIR=/mnt/p/Jules/Apps/NAIC
DB_FILE=/mnt/p/Jules/Apps/NAIC/data/naic_eu.db
```

## Probleemoplossing

| Probleem | Oplossing |
|----------|-----------|
| `/mnt/p` niet gemount | `sudo mount -a` of herstart NUC; check fstab |
| Permission denied op `/mnt/p/Jules/Apps/NAIC` | `sudo chown -R jules:jules /mnt/p/Jules/Apps/NAIC` |
| SSH geweigerd | `ssh jules@192.168.178.79` testen; check firewall |
| Yahoo timeout | Later opnieuw: `NAIC_DB_PATH=... .venv/bin/python run_etl.py` |
| TPCtoss-pad anders | Pas `APP_DIR` aan in `deploy/nuc6i5.env` |

## Servergegevens

| Item | Waarde |
|------|--------|
| Machine | Intel NUC6i5 |
| OS | Ubuntu 22.04 LTS |
| IP | 192.168.178.79 |
| Gebruiker | jules |
| App-pad | `/mnt/p/Jules/Apps/NAIC` |
| Database | `/mnt/p/Jules/Apps/NAIC/data/naic_eu.db` |
