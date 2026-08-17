#!/usr/bin/env bash
# Installeer NAIC EU-database op een Linux-systeem (NUC, VPS, etc.)
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/naic_db}"
REPO_URL="${REPO_URL:-https://github.com/Jules5235/sms.git}"
BRANCH="${BRANCH:-cursor/eu-naic-database-poc-d9c0}"
INSTALL_SYSTEMD="${INSTALL_SYSTEMD:-ask}"

log() { printf '\n[naic-install] %s\n' "$*"; }

need_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "Dit commando vereist sudo: $*"
        sudo "$@"
    else
        "$@"
    fi
}

install_system_packages() {
    if command -v apt-get >/dev/null 2>&1; then
        log "Systeempakketten installeren (python3-venv, git)..."
        need_root apt-get update -qq
        need_root apt-get install -y python3 python3-venv python3-pip git sqlite3
    elif command -v dnf >/dev/null 2>&1; then
        log "Systeempakketten installeren via dnf..."
        need_root dnf install -y python3 python3-pip git sqlite
    else
        log "Geen apt/dnf gevonden — controleer handmatig of python3 en git aanwezig zijn."
    fi
}

clone_or_update() {
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        log "Repository bijwerken in $INSTALL_DIR..."
        git -C "$INSTALL_DIR" fetch origin "$BRANCH"
        git -C "$INSTALL_DIR" checkout "$BRANCH"
        git -C "$INSTALL_DIR" pull origin "$BRANCH"
    elif [[ -f "$INSTALL_DIR/run_etl.py" ]]; then
        log "Bestaande installatie gevonden in $INSTALL_DIR (geen git) — overslaan clone."
    else
        log "Repository clonen naar $INSTALL_DIR..."
        git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$INSTALL_DIR"
    fi
}

setup_venv() {
    log "Python-omgeving opzetten..."
    cd "$INSTALL_DIR"
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
}

run_initial_etl() {
    log "Eerste ETL-draai starten (duurt ~1-2 minuten)..."
    cd "$INSTALL_DIR"
    .venv/bin/python run_etl.py
    log "Database aangemaakt: $INSTALL_DIR/data/naic_eu.db"
}

install_systemd_units() {
    local user="${SUDO_USER:-$USER}"
    local unit_dir="/etc/systemd/system"

    log "Systemd units installeren voor gebruiker $user..."
    need_root tee "$unit_dir/naic-etl.service" > /dev/null <<EOF
[Unit]
Description=NAIC EU stocks ETL (AEX + BEL20)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$user
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/run_etl.py
StandardOutput=journal
StandardError=journal
EOF

    need_root tee "$unit_dir/naic-etl.timer" > /dev/null <<EOF
[Unit]
Description=Wekelijkse NAIC ETL-update (zaterdag 07:00)

[Timer]
OnCalendar=Sat *-*-* 07:00:00
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF

    need_root systemctl daemon-reload
    need_root systemctl enable --now naic-etl.timer
    log "Timer actief: systemctl list-timers naic-etl.timer"
}

print_summary() {
    cat <<EOF

========================================
 NAIC-database geïnstalleerd
========================================
 Locatie:     $INSTALL_DIR
 Database:    $INSTALL_DIR/data/naic_eu.db
 Python venv: $INSTALL_DIR/.venv

 Handmatig draaien:
   cd $INSTALL_DIR
   .venv/bin/python run_etl.py
   .venv/bin/python query_ranking.py --index AEX

 Database inspecteren:
   sqlite3 $INSTALL_DIR/data/naic_eu.db "SELECT * FROM v_naic_ranking LIMIT 10;"

 Logs (als systemd actief):
   journalctl -u naic-etl.service -n 50

EOF
}

main() {
    install_system_packages
    clone_or_update
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
