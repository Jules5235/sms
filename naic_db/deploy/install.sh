#!/usr/bin/env bash
# Installeer NAIC EU-database op NUC6i5 (Ubuntu 22.04 LTS)
# Patroon: zelfde als TPCtoss.nl — app + data onder /mnt/p/Jules/Apps/NAIC
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Laad omgeving (lokaal op NUC of via deploy-remote.sh)
if [[ -f "$SCRIPT_DIR/nuc6i5.env" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/nuc6i5.env"
fi

INSTALL_DIR="${INSTALL_DIR:-${APP_DIR:-/mnt/p/Jules/Apps/NAIC}}"
DATA_DIR="${DATA_DIR:-$INSTALL_DIR/data}"
LOG_DIR="${LOG_DIR:-$INSTALL_DIR/logs}"
DB_FILE="${DB_FILE:-$DATA_DIR/naic_eu.db}"
REPO_URL="${REPO_URL:-https://github.com/Jules5235/sms.git}"
BRANCH="${BRANCH:-cursor/eu-naic-database-poc-d9c0}"
INSTALL_SYSTEMD="${INSTALL_SYSTEMD:-yes}"
SYSTEMD_SERVICE="${SYSTEMD_SERVICE:-naic-etl}"

export NAIC_DATA_DIR="$DATA_DIR"
export NAIC_DB_PATH="$DB_FILE"

log() { printf '\n[naic-install] %s\n' "$*"; }

need_root() {
    if [[ $EUID -ne 0 ]]; then
        sudo "$@"
    else
        "$@"
    fi
}

check_mount() {
    local mount_point
    mount_point="$(dirname "$(dirname "$INSTALL_DIR")")"  # /mnt/p/Jules
    if [[ "$INSTALL_DIR" == /mnt/p/* ]]; then
        if ! mountpoint -q /mnt/p 2>/dev/null; then
            log "WAARSCHUWING: /mnt/p is niet gemount. Controleer fstab (P:-schijf)."
            log "  Verwacht: P:/Jules/Apps/NAIC -> $INSTALL_DIR"
            if [[ "${FORCE_INSTALL:-}" != "1" ]]; then
                read -r -p "Toch doorgaan? [j/N] " answer
                [[ "$answer" =~ ^[jJyY]$ ]] || exit 1
            fi
        else
            log "P:-schijf gemount op /mnt/p — OK"
        fi
    fi
}

install_system_packages() {
    log "Systeempakketten installeren..."
    need_root apt-get update -qq
    need_root apt-get install -y python3 python3-venv python3-pip git sqlite3 rsync
}

sync_app_files() {
    local tmp_dir
    tmp_dir="$(mktemp -d)"
    trap 'rm -rf "$tmp_dir"' EXIT

    log "Code ophalen (branch $BRANCH)..."
    git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$tmp_dir/repo"

    log "Bestanden synchroniseren naar $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR"

    rsync -a --delete \
        --exclude '.venv' \
        --exclude 'data' \
        --exclude 'logs' \
        --exclude '__pycache__' \
        --exclude '.git' \
        "$tmp_dir/repo/naic_db/" "$INSTALL_DIR/"

    # Bewaar deploy-config in app-map
    cp "$SCRIPT_DIR/nuc6i5.env" "$INSTALL_DIR/deploy/nuc6i5.env"
}

setup_venv() {
    log "Python-omgeving opzetten in $INSTALL_DIR/.venv ..."
    cd "$INSTALL_DIR"
    if [[ ! -d .venv ]]; then
        python3 -m venv .venv
    fi
    .venv/bin/pip install --upgrade pip -q
    .venv/bin/pip install -r requirements.txt -q
}

run_initial_etl() {
    log "Eerste ETL-draai (duurt ~1-2 minuten)..."
    cd "$INSTALL_DIR"
    NAIC_DB_PATH="$DB_FILE" NAIC_DATA_DIR="$DATA_DIR" \
        .venv/bin/python run_etl.py 2>&1 | tee "$LOG_DIR/etl-$(date +%Y%m%d-%H%M%S).log"
    log "Database: $DB_FILE"
}

install_systemd_units() {
    local user="${SUDO_USER:-$USER}"
    local unit_dir="/etc/systemd/system"

    log "Systemd units installeren ($SYSTEMD_SERVICE)..."
    need_root tee "$unit_dir/${SYSTEMD_SERVICE}.service" > /dev/null <<EOF
[Unit]
Description=NAIC EU stocks ETL (AEX + BEL20)
After=network-online.target mnt-p.mount
Wants=network-online.target

[Service]
Type=oneshot
User=$user
WorkingDirectory=$INSTALL_DIR
Environment=NAIC_DB_PATH=$DB_FILE
Environment=NAIC_DATA_DIR=$DATA_DIR
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/run_etl.py
StandardOutput=append:$LOG_DIR/etl-systemd.log
StandardError=append:$LOG_DIR/etl-systemd.log
EOF

    need_root tee "$unit_dir/${SYSTEMD_SERVICE}.timer" > /dev/null <<EOF
[Unit]
Description=Wekelijkse NAIC ETL-update (zaterdag 07:00)

[Timer]
OnCalendar=${ETL_TIMER:-Sat *-*-* 07:00:00}
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF

    need_root systemctl daemon-reload
    need_root systemctl enable --now "${SYSTEMD_SERVICE}.timer"
    log "Timer actief: systemctl list-timers ${SYSTEMD_SERVICE}.timer"
}

print_summary() {
    cat <<EOF

========================================
 NAIC-database geïnstalleerd op ${NUC_NAME:-NUC}
========================================
 Server:      ${NUC_USER:-jules}@${NUC_HOST:-192.168.178.79}
 Windows:     P:/Jules/Apps/NAIC
 Linux:       $INSTALL_DIR
 Database:    $DB_FILE
 Logs:        $LOG_DIR

 Handmatig draaien:
   cd $INSTALL_DIR
   NAIC_DB_PATH=$DB_FILE .venv/bin/python run_etl.py
   NAIC_DB_PATH=$DB_FILE .venv/bin/python query_ranking.py --index AEX

 Database inspecteren:
   sqlite3 $DB_FILE "SELECT ticker, advice, win_loss_ratio FROM v_naic_ranking LIMIT 10;"

 Systemd:
   systemctl start ${SYSTEMD_SERVICE}.service
   journalctl -u ${SYSTEMD_SERVICE}.service -n 30

EOF
}

main() {
    check_mount
    install_system_packages
    sync_app_files
    setup_venv
    run_initial_etl

    case "$INSTALL_SYSTEMD" in
        yes|y|true|1)
            install_systemd_units
            ;;
        no|n|false|0)
            log "Systemd-timer overgeslagen."
            ;;
        ask|*)
            read -r -p "Wekelijkse systemd-timer installeren? [j/N] " answer
            if [[ "$answer" =~ ^[jJyY]$ ]]; then
                install_systemd_units
            fi
            ;;
    esac

    print_summary
}

main "$@"
