# Script to install ffmpeg on Windows

Write-Host "Installing FFmpeg..." -ForegroundColor Cyan

# Try winget first
Write-Host "Trying winget..." -ForegroundColor Yellow
try {
    winget install --id=Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    Write-Host "OK: FFmpeg installed via winget" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "winget failed, trying chocolatey..." -ForegroundColor Yellow
}

# Try chocolatey
try {
    choco install ffmpeg -y
    Write-Host "OK: FFmpeg installed via chocolatey" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "chocolatey failed" -ForegroundColor Yellow
}

Write-Host "ERROR: Could not install ffmpeg automatically" -ForegroundColor Red
Write-Host "Please install manually:" -ForegroundColor Yellow
Write-Host "1. Download from: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Cyan
Write-Host "2. Extract to C:\ffmpeg\" -ForegroundColor Cyan
Write-Host "3. Add C:\ffmpeg\bin to PATH" -ForegroundColor Cyan


