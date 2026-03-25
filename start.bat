@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════╗
echo ║       Kimi 2.5 CLI Agent - Docker Launcher        ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM .env dosyasi kontrolu
if not exist .env (
    echo [!] .env dosyasi bulunamadi
    echo [*] .env.example dosyasini .env olarak kopyaliyorum...
    copy .env.example .env >nul
    echo [!] Lutfen .env dosyasindaki MOONSHOT_API_KEY degerini ayarlayin!
    echo.
    notepad .env
    pause
    exit /b 1
)

REM Docker kontrolu
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Docker bulunamadi.
    echo [*] Docker Desktop yukleyin: https://docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Docker calisiyormu kontrol et
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Docker calismıyor. Docker Desktop'i baslatin.
    pause
    exit /b 1
)

echo [*] Eski container'lar temizleniyor...
docker-compose down --remove-orphans 2>nul

echo [*] Docker Compose baslatiliyor...
docker-compose up --build -d

if %errorlevel% neq 0 (
    echo [!] Docker Compose baslatılamadı!
    echo [*] Hata logları:
    docker-compose logs
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║              Servisler Baslatildi!                 ║
echo ╠════════════════════════════════════════════════════╣
echo ║  Frontend:  http://localhost:3000                  ║
echo ║  Backend:   http://localhost:8000                  ║
echo ║  API Docs:  http://localhost:8000/docs             ║
echo ╠════════════════════════════════════════════════════╣
echo ║  Durdurmak icin: docker-compose down               ║
echo ║  Loglar:         docker-compose logs -f            ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Tarayici ac
timeout /t 3 >nul
start http://localhost:3000

echo Logları görmek için Enter'a basın veya pencereyi kapatın...
pause >nul
docker-compose logs -f
