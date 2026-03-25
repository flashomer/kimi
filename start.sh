#!/bin/bash
echo "========================================"
echo "  Kimi 2.5 CLI Agent - Başlatılıyor"
echo "========================================"
echo

# .env dosyası kontrolü
if [ ! -f .env ]; then
    echo "[!] .env dosyası bulunamadı"
    echo "[*] .env.example dosyasını .env olarak kopyalıyorum..."
    cp .env.example .env
    echo "[!] Lütfen .env dosyasındaki MOONSHOT_API_KEY değerini ayarlayın!"
    exit 1
fi

# Docker kontrolü
if ! command -v docker &> /dev/null; then
    echo "[!] Docker bulunamadı. Lütfen Docker yükleyin."
    exit 1
fi

echo "[*] Docker Compose başlatılıyor..."
docker-compose up --build -d

echo
echo "========================================"
echo "  Servisler başlatıldı!"
echo "========================================"
echo
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo
echo "  Durdurmak için: docker-compose down"
echo "========================================"
