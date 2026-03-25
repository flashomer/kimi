#!/bin/bash
# Kimi CLI - Tek Komutla Kurulum
# curl -L raw.githubusercontent.com/user/kimi/main/install.sh | bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║           Kimi CLI - Kurulum Başlıyor                 ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[X] Python3 bulunamadı!${NC}"
    echo "Python 3.12+ yükleyin: https://python.org/downloads"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}[✓] Python $PYTHON_VERSION bulundu${NC}"

# pip kontrolü
if ! command -v pip3 &> /dev/null; then
    echo "[*] pip yükleniyor..."
    python3 -m ensurepip --upgrade
fi

# Bağımlılıkları yükle
echo "[*] Bağımlılıklar yükleniyor..."
pip3 install --quiet --upgrade openai rich requests

# Kimi CLI dizini
KIMI_DIR="$HOME/.kimi-cli"
mkdir -p "$KIMI_DIR"

# CLI'yı indir
echo "[*] Kimi CLI indiriliyor..."
REPO_URL="https://raw.githubusercontent.com/meczup/kimi/main"

curl -fsSL "$REPO_URL/kimi_cli.py" -o "$KIMI_DIR/kimi_cli.py" 2>/dev/null || \
wget -q "$REPO_URL/kimi_cli.py" -O "$KIMI_DIR/kimi_cli.py" 2>/dev/null || \
{
    # Fallback: yerel dosyayı kopyala
    if [ -f "./kimi_cli.py" ]; then
        cp ./kimi_cli.py "$KIMI_DIR/kimi_cli.py"
    else
        echo -e "${RED}[X] kimi_cli.py indirilemedi${NC}"
        exit 1
    fi
}

# Agent Swarm indir
curl -fsSL "$REPO_URL/agent_swarm.py" -o "$KIMI_DIR/agent_swarm.py" 2>/dev/null || \
cp ./agent_swarm.py "$KIMI_DIR/agent_swarm.py" 2>/dev/null || true

# Çalıştırılabilir script oluştur
cat > "$KIMI_DIR/kimi" << 'EOF'
#!/bin/bash
python3 "$HOME/.kimi-cli/kimi_cli.py" "$@"
EOF
chmod +x "$KIMI_DIR/kimi"

# PATH'e ekle
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "kimi-cli" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Kimi CLI" >> "$SHELL_RC"
        echo 'export PATH="$HOME/.kimi-cli:$PATH"' >> "$SHELL_RC"
    fi
fi

# Symlink oluştur
if [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
    ln -sf "$KIMI_DIR/kimi" /usr/local/bin/kimi 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Kurulum Tamamlandı!                         ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Kullanım:"
echo "  kimi              - CLI'yı başlat"
echo "  kimi --help       - Yardım"
echo "  kimi web          - Web arayüzünü aç"
echo ""
echo -e "${CYAN}Yeni terminal açın veya şunu çalıştırın:${NC}"
echo "  source $SHELL_RC"
echo ""
echo -e "${CYAN}Başlamak için:${NC} kimi"
