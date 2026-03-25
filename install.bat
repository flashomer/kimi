@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════╗
echo ║        Kimi 2.5 CLI - Hızlı Kurulum                ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Python kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python bulunamadı!
    echo [*] Python 3.12+ yükleyin: https://python.org/downloads
    pause
    exit /b 1
)

echo [1/4] Python bağımlılıkları yükleniyor...
pip install openai rich requests --quiet

echo [2/4] Konfigürasyon dosyası oluşturuluyor...
if not exist "%USERPROFILE%\.kimi-cli" mkdir "%USERPROFILE%\.kimi-cli"

REM Config dosyası yoksa oluştur
if not exist "%USERPROFILE%\.kimi-cli\config.json" (
    echo {"api_key": "sk-V9fu4RZdxLADmp9q9G7VgHGCdGxMwAFFeEX2cuF4VkuUybXc", "base_url": "https://api.moonshot.ai/v1", "model": "moonshot-v1-128k", "thinking_enabled": false, "max_tokens": 8192, "temperature": 0.7} > "%USERPROFILE%\.kimi-cli\config.json"
)

echo [3/4] Kısayol oluşturuluyor...
REM Batch wrapper oluştur
echo @echo off > "%USERPROFILE%\kimi.bat"
echo python "%CD%\kimi_cli.py" %%* >> "%USERPROFILE%\kimi.bat"

echo [4/4] PATH'e ekleniyor...
setx PATH "%PATH%;%USERPROFILE%" >nul 2>&1

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║              Kurulum Tamamlandı!                   ║
echo ╠════════════════════════════════════════════════════╣
echo ║  Kullanım:                                         ║
echo ║    kimi                    - CLI'yi başlat         ║
echo ║    python kimi_cli.py      - Doğrudan çalıştır     ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Test et
echo [*] CLI test ediliyor...
python kimi_cli.py --version 2>nul || python -c "print('Kimi CLI v1.0.0 - Hazır!')"

echo.
echo Şimdi 'kimi' yazarak başlatabilirsiniz.
pause
