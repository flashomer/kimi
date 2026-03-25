# Kimi CLI - Windows Kurulum
# irm https://flashomer.github.io/kimi/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host @"

   __ __ _           _    ___ __   ____
  / //_/(_)_ _  ____(_)  / __// /  /  _/
 / ,<  / /  ' \/ __/ /  / /_ / /__ / /
/_/|_|/_/_/_/_/\__/_/   \__//____/___/

  Kimi K2.5 CLI Agent

"@ -ForegroundColor Cyan

$REPO = "https://raw.githubusercontent.com/flashomer/kimi/master"
$INSTALL_DIR = "$env:USERPROFILE\.kimi"

# Python kontrolü
Write-Host "[1/4] Python kontrol ediliyor..."
try {
    $pyver = python --version 2>&1
    Write-Host "      $pyver OK" -ForegroundColor Green
} catch {
    Write-Host "[X] Python bulunamadi!" -ForegroundColor Red
    Write-Host "    Yukleyin: https://python.org/downloads"
    exit 1
}

# Bağımlılıklar
Write-Host "[2/4] Bagimliliklar yukleniyor..."
pip install --quiet --upgrade openai rich requests 2>$null

# Dizin oluştur
Write-Host "[3/4] Kimi CLI kuruluyor..."
New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null

# Dosyaları indir
Invoke-WebRequest -Uri "$REPO/kimi_cli.py" -OutFile "$INSTALL_DIR\kimi_cli.py"
try {
    Invoke-WebRequest -Uri "$REPO/agent_swarm.py" -OutFile "$INSTALL_DIR\agent_swarm.py" -ErrorAction SilentlyContinue
} catch {}

# Batch wrapper
@"
@echo off
python "%USERPROFILE%\.kimi\kimi_cli.py" %*
"@ | Out-File -FilePath "$INSTALL_DIR\kimi.bat" -Encoding ASCII

# PATH'e ekle
Write-Host "[4/4] PATH ayarlaniyor..."
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$INSTALL_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$INSTALL_DIR", "User")
    $env:Path = "$env:Path;$INSTALL_DIR"
}

Write-Host @"

========================================
  Kurulum tamamlandi!
========================================

  Yeni PowerShell penceresi acin ve:
    kimi

  Veya simdi calistirin:
    & "$INSTALL_DIR\kimi.bat"

"@ -ForegroundColor Green
