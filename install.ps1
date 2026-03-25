# Kimi CLI - Windows Kurulum
# irm https://flashomer.github.io/kimi/install.ps1 | iex

$ErrorActionPreference = "SilentlyContinue"

Write-Host @"

   __ __ _           _    ___ __   ____
  / //_/(_)_ _  ____(_)  / __// /  /  _/
 / ,<  / /  ' \/ __/ /  / /_ / /__ / /
/_/|_|/_/_/_/_/\__/_/   \__//____/___/

  Kimi K2.5 CLI Agent - Kurulum

"@ -ForegroundColor Cyan

$REPO = "https://raw.githubusercontent.com/flashomer/kimi/master"
$INSTALL_DIR = "$env:USERPROFILE\.kimi"

# Python kontrolu
Write-Host "[1/4] Python kontrol ediliyor..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "      [X] Python bulunamadi!" -ForegroundColor Red
    Write-Host "      Yukleyin: https://python.org/downloads" -ForegroundColor Gray
    exit 1
}
$pyver = & python --version 2>&1
Write-Host "      $pyver OK" -ForegroundColor Green

# Bagimliliklar
Write-Host "[2/4] Bagimliliklar yukleniyor..." -ForegroundColor Yellow
$null = & pip install --quiet --upgrade openai rich requests 2>&1
Write-Host "      OK" -ForegroundColor Green

# Dizin olustur
Write-Host "[3/4] Kimi CLI kuruluyor..." -ForegroundColor Yellow
$null = New-Item -ItemType Directory -Force -Path $INSTALL_DIR 2>&1

# Dosyalari indir
$null = Invoke-WebRequest -Uri "$REPO/kimi_cli.py" -OutFile "$INSTALL_DIR\kimi_cli.py" 2>&1
$null = Invoke-WebRequest -Uri "$REPO/agent_swarm.py" -OutFile "$INSTALL_DIR\agent_swarm.py" 2>&1
Write-Host "      OK" -ForegroundColor Green

# Batch wrapper
$batchContent = @"
@echo off
python "%USERPROFILE%\.kimi\kimi_cli.py" %*
"@
$batchContent | Out-File -FilePath "$INSTALL_DIR\kimi.bat" -Encoding ASCII

# PATH ekle
Write-Host "[4/4] PATH ayarlaniyor..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$INSTALL_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$INSTALL_DIR", "User")
    $env:Path = "$env:Path;$INSTALL_DIR"
}
Write-Host "      OK" -ForegroundColor Green

Write-Host @"

========================================
      Kurulum tamamlandi!
========================================

  Yeni terminal ac ve calistir:

    kimi

  Komutlar:
    kimi          - CLI baslat
    kimi web      - Web UI ac
    kimi --help   - Yardim

========================================

"@ -ForegroundColor Green
