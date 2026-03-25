# Kimi CLI - Windows PowerShell Kurulum
# Invoke-RestMethod https://raw.githubusercontent.com/user/kimi/main/install.ps1 | Invoke-Expression

$ErrorActionPreference = "Stop"

Write-Host @"
╔═══════════════════════════════════════════════════════╗
║           Kimi CLI - Windows Kurulum                  ║
╚═══════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Python kontrolü
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion bulundu" -ForegroundColor Green
} catch {
    Write-Host "[X] Python bulunamadi!" -ForegroundColor Red
    Write-Host "Python 3.12+ yukleyin: https://python.org/downloads"
    exit 1
}

# Bağımlılıkları yükle
Write-Host "[*] Bagimliliklar yukleniyor..."
pip install --quiet --upgrade openai rich requests

# Kimi dizini
$KIMI_DIR = "$env:USERPROFILE\.kimi-cli"
New-Item -ItemType Directory -Force -Path $KIMI_DIR | Out-Null

# Dosyaları kopyala
Write-Host "[*] Kimi CLI kuruluyor..."

$scriptPath = $PSScriptRoot
if (Test-Path "$scriptPath\kimi_cli.py") {
    Copy-Item "$scriptPath\kimi_cli.py" "$KIMI_DIR\kimi_cli.py" -Force
    Copy-Item "$scriptPath\agent_swarm.py" "$KIMI_DIR\agent_swarm.py" -Force -ErrorAction SilentlyContinue
} else {
    # GitHub'dan indir
    $repoUrl = "https://raw.githubusercontent.com/meczup/kimi/main"
    Invoke-WebRequest -Uri "$repoUrl/kimi_cli.py" -OutFile "$KIMI_DIR\kimi_cli.py"
    Invoke-WebRequest -Uri "$repoUrl/agent_swarm.py" -OutFile "$KIMI_DIR\agent_swarm.py" -ErrorAction SilentlyContinue
}

# Batch wrapper oluştur
@"
@echo off
python "%USERPROFILE%\.kimi-cli\kimi_cli.py" %*
"@ | Out-File -FilePath "$KIMI_DIR\kimi.bat" -Encoding ASCII

# PATH'e ekle
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$KIMI_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$KIMI_DIR", "User")
    $env:Path = "$env:Path;$KIMI_DIR"
}

Write-Host @"

╔═══════════════════════════════════════════════════════╗
║           Kurulum Tamamlandi!                         ║
╚═══════════════════════════════════════════════════════╝

Kullanim:
  kimi              - CLI'yi baslat
  kimi --help       - Yardim
  kimi web          - Web arayuzunu ac

Yeni PowerShell penceresi acin veya su komutu calistirin:
  refreshenv

Baslamak icin: kimi

"@ -ForegroundColor Green
