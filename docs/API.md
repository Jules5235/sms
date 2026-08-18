# NAIC API — endpoints

Basis-URL op NUC6i5: **http://192.168.178.79:8081**

Interactieve documentatie: **http://192.168.178.79:8081/docs**

## Endpoints

| Methode | Pad | Beschrijving |
|---------|-----|--------------|
| GET | `/health` | Status + database-info |
| GET | `/api/stats` | Aantal records per tabel |
| GET | `/api/ranking` | Ranking (filters: `?index=AEX`, `?advice=K`) |
| GET | `/api/ranking/{AEX\|BEL20}` | Ranking per index |
| GET | `/api/instruments` | Alle instrumenten (`?index=AEX`) |
| GET | `/api/instruments/{ticker}` | Detail + NAIC-score + fundamenten |
| GET | `/api/instruments/{ticker}/prices` | Koershistorie (`?limit=365`) |

## Voorbeelden

```bash
# Health check
curl http://192.168.178.79:8081/health

# AEX ranking, koopadviezen
curl "http://192.168.178.79:8081/api/ranking/AEX"
curl "http://192.168.178.79:8081/api/ranking?index=AEX&advice=K"

# ASML detail
curl http://192.168.178.79:8081/api/instruments/ASML

# Koersen afgelopen jaar
curl "http://192.168.178.79:8081/api/instruments/ASML/prices?limit=252"
```

## Python (voor je analyse-app)

```python
import requests

BASE = "http://192.168.178.79:8081"

ranking = requests.get(f"{BASE}/api/ranking/AEX", timeout=10).json()
koop = [r for r in ranking if r["advice"] == "K"]

asml = requests.get(f"{BASE}/api/instruments/ASML", timeout=10).json()
print(asml["naic_score"])
```

## Servicebeheer (NUC)

```bash
ssh jules@192.168.178.79
systemctl status naic-api.service
systemctl restart naic-api.service
journalctl -u naic-api.service -f
```

## Configuratie

In `deploy/nuc6i5.env`:

```
API_PORT=8081
```

Poort wijzigen vereist opnieuw deployen (`./deploy-remote.sh`).
