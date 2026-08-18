#!/usr/bin/env bash
# Deploy NAIC-database vanaf je laptop/PC naar NUC6i5 via SSH
# Gebruik: ./deploy-remote.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/nuc6i5.env"

TARGET="${NUC_USER}@${NUC_HOST}"
REMOTE_DEPLOY="/tmp/naic-deploy"

echo "==> Deploy NAIC naar $NUC_NAME ($TARGET)"
echo "    Doel: $APP_DIR (P:/Jules/Apps/NAIC)"

# Test SSH-verbinding
ssh -o ConnectTimeout=5 "$TARGET" "echo 'SSH OK — $(hostname)'" || {
    echo "Fout: kan niet verbinden met $TARGET"
    echo "Controleer: ssh $TARGET"
    exit 1
}

# Kopieer deploy-bestanden naar NUC
echo "==> Deploy-scripts kopieren..."
ssh "$TARGET" "mkdir -p $REMOTE_DEPLOY"
rsync -av "$SCRIPT_DIR/" "$TARGET:$REMOTE_DEPLOY/"

# Voer installatie uit op NUC
echo "==> Installatie starten op $NUC_NAME..."
ssh -t "$TARGET" "INSTALL_DIR='$APP_DIR' DATA_DIR='$DATA_DIR' LOG_DIR='$LOG_DIR' DB_FILE='$DB_FILE' INSTALL_SYSTEMD='$INSTALL_SYSTEMD' bash $REMOTE_DEPLOY/install.sh"

echo ""
echo "==> Deploy voltooid."
echo "    Database: $DB_FILE"
echo "    SSH:      ssh $TARGET"
echo "    Ranking:  ssh $TARGET 'cd $APP_DIR && NAIC_DB_PATH=$DB_FILE .venv/bin/python query_ranking.py --index AEX'"
