# NAIC-database opzetten op je NUC7i5

Stappenplan voor een Intel NUC (of vergelijkbare thuisserver) met **Ubuntu/Debian Linux**.

## Vereisten

| Component | Minimum | Jouw NUC7i5 |
|-----------|---------|-------------|
| RAM | 1 GB vrij | Ruim voldoende (typisch 8–16 GB) |
| Opslag | ~500 MB | Geen probleem |
| Netwerk | Internet voor Yahoo/Stooq | Vereist |
| OS | Linux met Python 3.10+ | Ubuntu 22.04/24.04 aanbevolen |

## Optie A — Automatische installatie (aanbevolen)

SSH naar je NUC en voer uit:

```bash
curl -fsSL https://raw.githubusercontent.com/Jules5235/sms/cursor/eu-naic-database-poc-d9c0/naic_db/deploy/install.sh -o /tmp/naic-install.sh
chmod +x /tmp/naic-install.sh
INSTALL_DIR=$HOME/naic_db /tmp/naic-install.sh
```

Het script doet het volgende:
1. Installeert `python3-venv`, `git`, `sqlite3`
2. Clone de repository naar `~/naic_db`
3. Maakt een Python virtual environment aan
4. Draait de eerste ETL (~1–2 minuten)
5. Vraagt of je een wekelijkse systemd-timer wilt (zaterdag 07:00)

### Aangepaste installatielocatie

```bash
INSTALL_DIR=/opt/naic_db INSTALL_SYSTEMD=yes /tmp/naic-install.sh
```

## Optie B — Handmatige installatie

```bash
# 1. Systeempakketten
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git sqlite3

# 2. Code ophalen
git clone --branch cursor/eu-naic-database-poc-d9c0 \
  https://github.com/Jules5235/sms.git /tmp/sms
cp -r /tmp/sms/naic_db ~/naic_db
cd ~/naic_db

# 3. Python-omgeving
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Database vullen
python run_etl.py

# 5. Resultaat bekijken
python query_ranking.py --index AEX
```

## Wekelijkse automatische update

Na installatie met systemd:

```bash
# Status timer
systemctl list-timers naic-etl.timer

# Handmatig nu draaien
systemctl start naic-etl.service

# Logs bekijken
journalctl -u naic-etl.service -f
```

Zonder systemd (cron):

```bash
crontab -e
# Voeg toe:
0 7 * * 6  /home/jouwgebruiker/naic_db/.venv/bin/python /home/jouwgebruiker/naic_db/run_etl.py >> /home/jouwgebruiker/naic_db/data/etl.log 2>&1
```

## Database benaderen vanaf andere apparaten

De SQLite-database staat op:
```
~/naic_db/data/naic_eu.db
```

### Optie 1 — SSH + sqlite3 (eenvoudigst)

Vanaf je laptop:
```bash
ssh gebruiker@nuc-ip "sqlite3 ~/naic_db/data/naic_eu.db 'SELECT ticker, advice, win_loss_ratio FROM v_naic_ranking WHERE index_code=\"AEX\" LIMIT 10;'"
```

### Optie 2 — Samba/NFS share

Deel de map `~/naic_db/data/` via Samba zodat je de database vanaf Windows/Mac kunt openen met DB Browser for SQLite.

### Optie 3 — Later: PostgreSQL + web-UI

Voor meerdere gebruikers of een dashboard is PostgreSQL een logische volgende stap (nog niet in deze PoC).

## Controle na installatie

```bash
cd ~/naic_db

# Aantal records
sqlite3 data/naic_eu.db "
  SELECT 'instrumenten', COUNT(*) FROM instruments
  UNION ALL SELECT 'koersen', COUNT(*) FROM price_daily
  UNION ALL SELECT 'fundamenten', COUNT(*) FROM fundamentals_annual
  UNION ALL SELECT 'naic_scores', COUNT(*) FROM naic_scores;
"

# Verwacht: ~45 instrumenten, ~120k koersen, ~210 fundamenten, 45 scores
```

## Probleemoplossing

| Probleem | Oplossing |
|----------|-----------|
| `python3-venv` niet gevonden | `sudo apt install python3-venv` |
| Yahoo timeout / lege data | Later opnieuw draaien: `python run_etl.py` |
| Stooq daglimiet | Wacht 24 uur of gebruik alleen Yahoo |
| Permission denied op data/ | `chmod 755 ~/naic_db/data` |
| Git branch niet gevonden | Controleer of PR #1 is gemerged; pas `BRANCH` aan in install.sh |

## Home Assistant OS?

Als je NUC Home Assistant OS draait (geen volledige Linux-shell), installeer de database op een **aparte machine/VM** of gebruik de **HA Terminal & SSH add-on** met beperkte mogelijkheden. Een dedicated Ubuntu-installatie op de NUC is het eenvoudigst.

## Volgende stap

Zodra de database draait op je NUC, kun je:
- ESEF/XBRL toevoegen voor betere fundamenten
- Een eenvoudig webdashboard koppelen
- Alerts instellen bij koopadvies (K)
