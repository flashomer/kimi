#!/bin/bash
# Kimi CLI - Tek Komutla Kurulum
# curl -fsSL https://flashomer.github.io/kimi/install.sh | bash

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

REPO="https://raw.githubusercontent.com/flashomer/kimi/master"
INSTALL_DIR="$HOME/.kimi"

echo -e "${CYAN}"
cat << 'EOF'
   __ __ _           _    ___ __   ____
  / //_/(_)_ _  ____(_)  / __// /  /  _/
 / ,<  / /  ' \/ __/ /  / /_ / /__ / /
/_/|_|/_/_/_/_/\__/_/   \__//____/___/

EOF
echo -e "Kimi K2.5 CLI Agent${NC}"
echo ""

# Python kontrolü
echo -e "[1/4] Python kontrol ediliyor..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[X] Python3 bulunamadı!${NC}"
    echo "    Yükleyin: https://python.org/downloads"
    exit 1
fi
PYVER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}      Python $PYVER OK${NC}"

# Bağımlılıklar
echo -e "[2/4] Bağımlılıklar yükleniyor..."
pip3 install --quiet --upgrade openai rich requests 2>/dev/null || pip install --quiet --upgrade openai rich requests

# Dizin oluştur
echo -e "[3/4] Kimi CLI kuruluyor..."
mkdir -p "$INSTALL_DIR"

# Dosyaları indir
curl -fsSL "$REPO/kimi_cli.py" -o "$INSTALL_DIR/kimi_cli.py"
curl -fsSL "$REPO/agent_swarm.py" -o "$INSTALL_DIR/agent_swarm.py" 2>/dev/null || true

# Çalıştırıcı oluştur
cat > "$INSTALL_DIR/kimi" << 'RUNNER'
#!/bin/bash
python3 "$HOME/.kimi/kimi_cli.py" "$@"
RUNNER
chmod +x "$INSTALL_DIR/kimi"

# PATH'e ekle
echo -e "[4/4] PATH ayarlanıyor..."
SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if ! grep -q ".kimi" "$SHELL_RC" 2>/dev/null; then
    echo '' >> "$SHELL_RC"
    echo '# Kimi CLI' >> "$SHELL_RC"
    echo 'export PATH="$HOME/.kimi:$PATH"' >> "$SHELL_RC"
fi

# Symlink
[ -w /usr/local/bin ] && ln -sf "$INSTALL_DIR/kimi" /usr/local/bin/kimi 2>/dev/null || true

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Kurulum tamamlandı!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "  Başlatmak için:"
echo -e "    ${CYAN}source $SHELL_RC${NC}"
echo -e "    ${CYAN}kimi${NC}"
echo ""
echo "  Veya yeni terminal açın ve:"
echo -e "    ${CYAN}kimi${NC}"
echo ""
