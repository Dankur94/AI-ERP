#!/bin/bash
# AI ERP ??Git-based Deploy Script
# Workflow: git push lokal -> VM pullt von GitHub -> Service restart -> Health-Check

set -e

VM_HOST=""
VM_PATH="/"
SSH_KEY="$HOME/"
SERVICE_NAME=""
HEALTH_PORT="8000"
DB_NAME=""
BACKUP_DIR="./backups"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "==============================="
echo " AI ERP ??Git Deploy"
echo "==============================="
echo ""

# --- Preflight checks ---
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}[FEHLER] SSH Key nicht gefunden: $SSH_KEY${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] SSH Key gefunden${NC}"

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${YELLOW}[WARNUNG] Uncommitted Changes:${NC}"
    git status --short
    echo ""
    read -p "Trotzdem deployen (nur committed Code)? (y/N): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "Abbruch. Bitte erst committen."
        exit 1
    fi
fi

# Push to GitHub
LOCAL_HEAD=$(git rev-parse HEAD)
REMOTE_HEAD=$(git rev-parse origin/main 2>/dev/null || echo "unknown")

if [ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]; then
    echo -e "${YELLOW}Pushe lokale Commits...${NC}"
    git push origin main
    echo -e "${GREEN}[OK] Code gepusht${NC}"
else
    echo -e "${GREEN}[OK] GitHub ist aktuell${NC}"
fi

# --- VM: Clone or Pull ---
echo ""
VM_HAS_REPO=$(ssh -i "$SSH_KEY" "$VM_HOST" "test -d ${VM_PATH}.git && echo 'yes' || echo 'no'" 2>/dev/null)

if [ "$VM_HAS_REPO" = "no" ]; then
    echo -e "${YELLOW}Erster Deploy ??klone Repo auf VM...${NC}"

    # Swap einrichten (t3.micro hat nur 1GB RAM)
    HAS_SWAP=$(ssh -i "$SSH_KEY" "$VM_HOST" "swapon --show | wc -l" 2>/dev/null)
    if [ "$HAS_SWAP" -le 1 ]; then
        echo "Richte 1GB Swap ein..."
        ssh -i "$SSH_KEY" "$VM_HOST" "sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile && echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab" 2>/dev/null
        echo -e "${GREEN}[OK] 1GB Swap eingerichtet${NC}"
    else
        echo -e "${GREEN}[OK] Swap bereits vorhanden${NC}"
    fi

    # Backup existing files
    ssh -i "$SSH_KEY" "$VM_HOST" "mkdir -p /tmp/deploy-backup && cp ${VM_PATH}config.yaml /tmp/deploy-backup/ 2>/dev/null || true"
    # Clone
    REPO_URL=$(git remote get-url origin)
    ssh -i "$SSH_KEY" "$VM_HOST" "rm -rf ${VM_PATH} && git clone $REPO_URL ${VM_PATH}"
    # Restore config
    ssh -i "$SSH_KEY" "$VM_HOST" "cp /tmp/deploy-backup/config.yaml ${VM_PATH} 2>/dev/null || true"
    echo -e "${GREEN}[OK] Repo geklont + Config wiederhergestellt${NC}"
else
    echo "Pulle neusten Code..."
    ssh -i "$SSH_KEY" "$VM_HOST" "cd ${VM_PATH} && git fetch origin && git reset --hard origin/main"
    echo -e "${GREEN}[OK] VM aktualisiert${NC}"
fi

# --- Verify config.yaml ---
echo ""
VM_HAS_CONFIG=$(ssh -i "$SSH_KEY" "$VM_HOST" "test -f ${VM_PATH}config.yaml && echo 'yes' || echo 'no'" 2>/dev/null)
if [ "$VM_HAS_CONFIG" = "no" ]; then
    echo -e "${RED}[FEHLER] config.yaml fehlt auf VM!${NC}"
    echo "  Kopiere config.example.yaml und trage echte Werte ein:"
    echo "  ssh -i $SSH_KEY $VM_HOST 'cd $VM_PATH && cp config.example.yaml config.yaml && nano config.yaml'"
    exit 1
fi
echo -e "${GREEN}[OK] config.yaml vorhanden${NC}"

# --- Backup config.yaml von VM ---
echo ""
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
scp -i "$SSH_KEY" "$VM_HOST:${VM_PATH}config.yaml" "$BACKUP_DIR/config.yaml.${TIMESTAMP}" 2>/dev/null
if [ $? -eq 0 ]; then
    cp "$BACKUP_DIR/config.yaml.${TIMESTAMP}" "$BACKUP_DIR/config.yaml.latest"
    echo -e "${GREEN}[OK] config.yaml gesichert (backups/config.yaml.${TIMESTAMP})${NC}"
else
    echo -e "${YELLOW}[WARN] config.yaml Backup fehlgeschlagen${NC}"
fi

# --- Backup Datenbank von VM ---
if [ -n "$DB_NAME" ]; then
    ssh -i "$SSH_KEY" "$VM_HOST" "cd ${VM_PATH} && sqlite3 ${DB_NAME} '.backup /tmp/${DB_NAME}.backup'" 2>/dev/null
    scp -i "$SSH_KEY" "$VM_HOST:/tmp/${DB_NAME}.backup" "$BACKUP_DIR/${DB_NAME}.${TIMESTAMP}" 2>/dev/null
    if [ $? -eq 0 ]; then
        cp "$BACKUP_DIR/${DB_NAME}.${TIMESTAMP}" "$BACKUP_DIR/${DB_NAME}.latest"
        echo -e "${GREEN}[OK] Datenbank gesichert (backups/${DB_NAME}.${TIMESTAMP})${NC}"
    else
        echo -e "${YELLOW}[WARN] DB-Backup fehlgeschlagen${NC}"
    fi
fi

# --- Restart service ---
if [ -n "$SERVICE_NAME" ]; then
    echo ""
    echo "Starte $SERVICE_NAME neu..."
    ssh -i "$SSH_KEY" "$VM_HOST" "sudo systemctl restart $SERVICE_NAME"
    echo -e "${GREEN}[OK] $SERVICE_NAME neu gestartet${NC}"

    # Health-Check (falls /health endpoint existiert)
    sleep 3
    echo "Health-Check..."
    HEALTH=$(ssh -i "$SSH_KEY" "$VM_HOST" "curl -s http://localhost:${HEALTH_PORT}/health" 2>/dev/null || echo "")
    if echo "$HEALTH" | grep -q '"status"'; then
        echo -e "${GREEN}[OK] Health Check bestanden${NC}"
    elif [ -z "$HEALTH" ]; then
        echo -e "${YELLOW}[INFO] Kein /health Endpoint gefunden ??manuell pruefen${NC}"
    else
        echo -e "${RED}[FEHLER] Health Check fehlgeschlagen: $HEALTH${NC}"
        exit 1
    fi
fi

# Show deployed commit
DEPLOYED=$(ssh -i "$SSH_KEY" "$VM_HOST" "cd ${VM_PATH} && git log --oneline -1" 2>/dev/null)
echo ""
echo "==============================="
echo -e "${GREEN} Deploy erfolgreich!${NC}"
echo "  Deployed: $DEPLOYED"
echo "==============================="
