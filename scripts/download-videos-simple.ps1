# Script to download videos with human-readable names
# Downloads best quality in mp4
# Uses video-metadata.json to get file names

$downloadDir = "downloaded_videos"
if (-not (Test-Path $downloadDir)) {
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
}

# Check for yt-dlp
try {
    python -m yt_dlp --version | Out-Null
} catch {
    Write-Host "yt-dlp not found. Installing..." -ForegroundColor Yellow
    python -m pip install --upgrade yt-dlp
}

# Read metadata
$metadataFile = "video-metadata.json"
if (-not (Test-Path $metadataFile)) {
    Write-Host "Error: file $metadataFile not found!" -ForegroundColor Red
    exit 1
}

$json = Get-Content $metadataFile -Raw -Encoding UTF8 | ConvertFrom-Json

Write-Host "Downloading $($json.videos.Count) videos..." -ForegroundColor Cyan
Write-Host "Folder: $((Get-Location).Path)\$downloadDir`n" -ForegroundColor Gray

$count = 0
foreach ($video in $json.videos) {
    $count++
    $filename = "$($video.filename).mp4"
    $filepath = Join-Path $downloadDir $filename
    
    # Check if already downloaded
    if (Test-Path $filepath) {
        Write-Host "[$count/$($json.videos.Count)] Skip: $filename (already downloaded)" -ForegroundColor Gray
        continue
    }
    
    Write-Host "[$count/$($json.videos.Count)] Downloading: $($video.video_id)" -ForegroundColor Yellow
    Write-Host "  Saving as: $filename" -ForegroundColor Gray
    
    python -m yt_dlp -f "best[ext=mp4]/best" "https://www.youtube.com/watch?v=$($video.video_id)" -o $filepath --no-warnings
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Done: $filename" -ForegroundColor Green
    } else {
        Write-Host "  Error downloading $($video.video_id)" -ForegroundColor Red
    }
}

$downloadedCount = (Get-ChildItem $downloadDir\*.mp4 -ErrorAction SilentlyContinue).Count
Write-Host ""
Write-Host "Done! Videos saved in folder: $downloadDir" -ForegroundColor Green
Write-Host "Total files: $downloadedCount" -ForegroundColor Gray
