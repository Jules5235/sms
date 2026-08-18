#!/usr/bin/env bash
# Deploy broncode van P:\Jules\Apps\NAIC naar NUC6i5
# Synct ALLEEN code — productiedatabase op NUC blijft intact
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/nuc6i5.env"

TARGET="${NUC_USER}@${NUC_HOST}"

echo "=========================================="
echo " NAIC deploy: PC → NUC6i5"
echo "=========================================="
echo " Bron (dev):  $PACKAGE_ROOT"
echo "             (verwacht: P:/Jules/Apps/NAIC)"
echo " Doel (prod): $APP_DIR"
echo " Database:    $DB_FILE  (wordt NIET overschreven)"
echo ""

ssh -o ConnectTimeout=5 "$TARGET" "echo SSH OK — \$(hostname)"

sync_code() {
    local excludes=(
        --exclude '.venv/'
        --exclude 'data/'
        --exclude 'logs/'
        --exclude '__pycache__/'
        --exclude '*.egg-info/'
        --exclude '.git/'
        --exclude 'manual-install/'
    )

    if command -v rsync >/dev/null 2>&1; then
        rsync -av "${excludes[@]}" "$PACKAGE_ROOT/" "$TARGET:$APP_DIR/"
        return
    fi

    echo "    rsync niet gevonden — fallback via tar+scp (Git Bash/Windows)"
    local archive="/tmp/naic-deploy-$$.tgz"
    tar -czf "$archive" -C "$PACKAGE_ROOT" \
        --exclude='.venv' --exclude='data' --exclude='logs' \
        --exclude='__pycache__' --exclude='*.egg-info' --exclude='.git' \
        --exclude='manual-install' .
    scp "$archive" "$TARGET:/tmp/naic-deploy.tgz"
    rm -f "$archive"
    ssh "$TARGET" "mkdir -p '$APP_DIR' && tar -xzf /tmp/naic-deploy.tgz -C '$APP_DIR' && rm -f /tmp/naic-deploy.tgz"
}

echo "==> Code synchroniseren (data/ en logs/ blijven op NUC)..."
sync_code

echo "==> App bijwerken op NUC (venv + ETL)..."
ssh -t "$TARGET" "cd '$APP_DIR' && SKIP_ETL=${SKIP_ETL:-0} bash deploy/install.sh"

echo ""
echo "==> Deploy voltooid."
echo "    Database op NUC: $DB_FILE"
echo ""
echo " Ranking bekijken:"
echo "   ssh $TARGET 'cd $APP_DIR && .venv/bin/naic-ranking --index AEX'"
echo ""
echo " REST API (na deploy):"
echo "   http://${NUC_HOST}:${API_PORT:-8080}/health"
echo "   http://${NUC_HOST}:${API_PORT:-8080}/docs"
echo ""
echo " Voor je analyse-app: zie docs/API.md"
