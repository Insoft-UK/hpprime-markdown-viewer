# Deploy HP Prime app to target directories
$ErrorActionPreference = "Stop"

$appName = "MarkdownViewer.hpappdir"

$source = Join-Path $PSScriptRoot $appName

$targets = @(
    "$env:USERPROFILE\Documents\HP Connectivity Kit\Calculators\HP Prime\$appName",
    "$env:USERPROFILE\Documents\HP Connectivity Kit\Content\$appName",
    "$env:USERPROFILE\Documents\HP Prime\Calculators\Prime\$appName"
)

$apps = @(
    "C:\Program Files\HP\HP Prime Virtual Calculator\HPPrime.exe",
    "C:\Program Files\HP\HP Connectivity Kit\ConnectivityKit.exe"
)

if (-not (Test-Path $source)) {
    Write-Error "Source not found: $source"
    exit 1
}

# Stop HP processes
foreach ($app in $apps) {
    $procName = [System.IO.Path]::GetFileNameWithoutExtension($app)
    $proc = Get-Process -Name $procName -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "Stopping $procName" -ForegroundColor Yellow
        $proc | Stop-Process -Force
        $proc | Wait-Process -ErrorAction SilentlyContinue
    }
}

foreach ($target in $targets) {
    if (Test-Path $target) {
        Write-Host "Removing $target" -ForegroundColor Yellow
        Remove-Item -Path $target -Recurse -Force
    }

    $parentDir = Split-Path $target -Parent
    if (-not (Test-Path $parentDir)) {
        Write-Host "Creating parent directory: $parentDir" -ForegroundColor Cyan
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    Write-Host "Copying to $target" -ForegroundColor Green
    Copy-Item -Path $source -Destination $target -Recurse -Force
}

# Restart HP processes
foreach ($app in $apps) {
    if (Test-Path $app) {
        Write-Host "Starting $app" -ForegroundColor Cyan
        Start-Process -FilePath $app
    }
}

Write-Host "`nDeployment complete." -ForegroundColor Green
