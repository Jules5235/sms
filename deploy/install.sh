#!/usr/bin/env bash
# Installeer/update NAIC op NUC6i5 (productie)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$SCRIPT_DIR/nuc6i5.env" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/nuc6i5.env"
fi

INSTALL_DIR="${INSTALL_DIR:-${APP_DIR:-/home/jules/naic}}"
DATA_DIR="${DATA_DIR:-$INSTALL_DIR/data}"
LOG_DIR="${LOG_DIR:-$INSTALL_DIR/logs}"
DB_FILE="${DB_FILE:-$DATA_DIR/naic_eu.db}"
SOURCE_DIR="${SOURCE_DIR:-$PACKAGE_ROOT}"
INSTALL_SYSTEMD="${INSTALL_SYSTEMD:-yes}"
SYSTEMD_SERVICE="${SYSTEMD_SERVICE:-naic-etl}"
API_SERVICE="${API_SERVICE:-naic-api}"
API_PORT="${API_PORT:-8080}"
SKIP_ETL="${SKIP_ETL:-0}"

export NAIC_APP_DIR="$INSTALL_DIR"
export NAIC_DATA_DIR="$DATA_DIR"
export NAIC_DB_PATH="$DB_FILE"
export NAIC_LOG_DIR="$LOG_DIR"

log() { printf '\n[naic-install] %s\n' "$*"; }

need_root() {
    if [[ $EUID -ne 0 ]]; then sudo "$@"; else "$@"; fi
}

install_system_packages() {
    if command -v apt-get >/dev/null 2>&1; then
        log "Systeempakketten controleren..."
        need_root apt-get update -qq
        need_root apt-get install -y python3 python3-venv python3-pip sqlite3 rsync
    fi
}

sync_app_files() {
    if [[ "$SOURCE_DIR" != "$INSTALL_DIR" ]]; then
        log "Kopiëren van $SOURCE_DIR naar $INSTALL_DIR..."
        mkdir -p "$INSTALL_DIR"
        rsync -a \
            --exclude '.venv' --exclude 'data' --exclude 'logs' \
            --exclude '__pycache__' --exclude '*.egg-info' --exclude '.git' \
            "$SOURCE_DIR/" "$INSTALL_DIR/"
    fi
    mkdir -p "$DATA_DIR" "$LOG_DIR"
}

setup_venv() {
    log "Python-omgeving opzetten..."
    cd "$INSTALL_DIR"
    [[ -d .venv ]] || python3 -m venv .venv
    .venv/bin/pip install --upgrade pip -q
    .venv/bin/pip install -e . -q
}

run_etl() {
    if [[ "$SKIP_ETL" == "1" ]]; then
        log "ETL overgeslagen (SKIP_ETL=1)."
        return
    fi
    log "ETL draaien..."
    cd "$INSTALL_DIR"
    NAIC_APP_DIR="$INSTALL_DIR" NAIC_DB_PATH="$DB_FILE" NAIC_DATA_DIR="$DATA_DIR" \
        .venv/bin/naic-etl 2>&1 | tee "$LOG_DIR/etl-$(date +%Y%m%d-%H%M%S).log"
}

install_systemd_units() {
    local user="${SUDO_USER:-$USER}"
    log "Systemd timer installeren..."
    need_root tee "/etc/systemd/system/${SYSTEMD_SERVICE}.service" > /dev/null <<EOF
[Unit]
Description=NAIC EU stocks ETL (AEX + BEL20)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$user
WorkingDirectory=$INSTALL_DIR
Environment=NAIC_APP_DIR=$INSTALL_DIR
Environment=NAIC_DB_PATH=$DB_FILE
Environment=NAIC_DATA_DIR=$DATA_DIR
ExecStart=$INSTALL_DIR/.venv/bin/naic-etl
StandardOutput=append:$LOG_DIR/etl-systemd.log
StandardError=append:$LOG_DIR/etl-systemd.log
EOF

    need_root tee "/etc/systemd/system/${SYSTEMD_SERVICE}.timer" > /dev/null <<EOF
[Unit]
Description=Wekelijkse NAIC ETL (zaterdag 07:00)
[Timer]
OnCalendar=${ETL_TIMER:-Sat *-*-* 07:00:00}
Persistent=true
RandomizedDelaySec=300
[Install]
WantedBy=timers.target
EOF

    need_root systemctl daemon-reload
    need_root systemctl enable --now "${SYSTEMD_SERVICE}.timer"
}

install_api_service() {
    local user="${SUDO_USER:-$USER}"
    log "REST API service installeren (poort $API_PORT)..."
    need_root tee "/etc/systemd/system/${API_SERVICE}.service" > /dev/null <<EOF
[Unit]
Description=NAIC EU REST API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$user
WorkingDirectory=$INSTALL_DIR
Environment=NAIC_APP_DIR=$INSTALL_DIR
Environment=NAIC_DB_PATH=$DB_FILE
Environment=NAIC_DATA_DIR=$DATA_DIR
Environment=NAIC_API_HOST=0.0.0.0
Environment=NAIC_API_PORT=$API_PORT
ExecStart=$INSTALL_DIR/.venv/bin/naic-api
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    need_root systemctl daemon-reload
    need_root systemctl enable --now "${API_SERVICE}.service"
}

print_summary() {
    cat <<EOF

========================================
 NAIC productie op NUC6i5
========================================
 App:       $INSTALL_DIR
 Database:  $DB_FILE
 Logs:      $LOG_DIR

 ETL:       systemctl start ${SYSTEMD_SERVICE}.service
 Ranking:   cd $INSTALL_DIR && .venv/bin/naic-ranking --index AEX
 Timer:     systemctl list-timers ${SYSTEMD_SERVICE}.timer
 API:       http://${NUC_HOST:-192.168.178.79}:${API_PORT}/health
 Docs:      http://${NUC_HOST:-192.168.178.79}:${API_PORT}/docs

EOF
}

main() {
    install_system_packages
    sync_app_files
    setup_venv
    run_etl
    case "$INSTALL_SYSTEMD" in yes|y|true|1)
        install_systemd_units
        install_api_service
        ;;
    esac
    print_summary
}

main "$@"
