<#
.SYNOPSIS
  Check which environment (local vs cloud) each part of DoctorScribe points to.

.DESCRIPTION
  Reads .env files, container env vars, and live API responses to verify
  that the LOCAL stack is fully isolated from the CLOUD stack.

.USAGE
  cd c:\Doctor-Scribe
  powershell -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
#>

$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent $PSScriptRoot

function Write-Section($title) {
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Get-EnvValue($file, $key) {
    if (-not (Test-Path $file)) { return $null }
    $line = Select-String -Path $file -Pattern "^\s*$key\s*=" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $line) { return $null }
    return ($line.Line -split '=', 2)[1].Trim().Trim('"').Trim("'")
}

function Show-Status($label, $value, $expectedLocal) {
    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Host "  $label" -NoNewline
        Write-Host "  (not set)" -ForegroundColor DarkGray
        return
    }
    $isLocal = $value -match 'localhost|127\.0\.0\.1|host\.docker\.internal|^postgres$|^backend$|^redis$|^minio$'
    $color = if ($isLocal -eq $expectedLocal) { 'Green' } else { 'Red' }
    $tag   = if ($isLocal) { '[LOCAL]' } else { '[CLOUD]' }
    Write-Host "  $label" -NoNewline
    Write-Host "  $tag $value" -ForegroundColor $color
}

# ----------------------------------------------------------------------
Write-Section "1. parent-website (Next.js)  -> localhost:3001"
$envLocal = Join-Path $repo 'parent-website\.env.local'
$envProd  = Join-Path $repo 'parent-website\.env'
foreach ($f in @($envLocal, $envProd)) {
    if (Test-Path $f) {
        Write-Host ""
        Write-Host "  File: $f" -ForegroundColor Yellow
        Show-Status "NEXT_PUBLIC_API_URL    :" (Get-EnvValue $f 'NEXT_PUBLIC_API_URL') $true
        Show-Status "NEXT_PUBLIC_SITE_URL   :" (Get-EnvValue $f 'NEXT_PUBLIC_SITE_URL') $true
    }
}

# ----------------------------------------------------------------------
Write-Section "2. backend (FastAPI)  -> localhost:8000"
$envBackend = Join-Path $repo '.env'
if (Test-Path $envBackend) {
    Write-Host "  File: $envBackend" -ForegroundColor Yellow
    Show-Status "POSTGRES_HOST          :" (Get-EnvValue $envBackend 'POSTGRES_HOST') $true
    Show-Status "REDIS_HOST             :" (Get-EnvValue $envBackend 'REDIS_HOST')    $true
    Show-Status "MINIO_ENDPOINT         :" (Get-EnvValue $envBackend 'MINIO_ENDPOINT') $true
    Show-Status "FRONTEND_URL           :" (Get-EnvValue $envBackend 'FRONTEND_URL')  $true
    Show-Status "BACKEND_URL            :" (Get-EnvValue $envBackend 'BACKEND_URL')   $true
}

# ----------------------------------------------------------------------
Write-Section "3. Live containers (docker-compose)"
try {
    $containers = docker compose ps --format json 2>$null | ConvertFrom-Json
    if (-not $containers) { $containers = docker-compose ps --format json 2>$null | ConvertFrom-Json }
    foreach ($c in $containers) {
        Write-Host ("  {0,-25} {1}" -f $c.Service, $c.State) -ForegroundColor Gray
    }
} catch {
    Write-Host "  (docker not running or no containers)" -ForegroundColor DarkGray
}

# ----------------------------------------------------------------------
Write-Section "4. Live API check  (counts must DIFFER for true isolation)"
function Try-Api($url) {
    try {
        $r = Invoke-RestMethod -Uri $url -TimeoutSec 5 -ErrorAction Stop
        $items = if ($r.items) { $r.items } elseif ($r -is [array]) { $r } else { @() }
        return $items.Count
    } catch {
        return "ERROR: $($_.Exception.Message.Split([char]10)[0])"
    }
}
$localCount = Try-Api 'http://localhost:8000/api/articles'
$cloudCount = Try-Api 'https://app.drsscribe.com/api/articles'
Write-Host "  LOCAL  http://localhost:8000/api/articles      -> $localCount articles" -ForegroundColor $(if ($localCount -is [int]) {'Green'} else {'Red'})
Write-Host "  CLOUD  https://app.drsscribe.com/api/articles  -> $cloudCount articles" -ForegroundColor $(if ($cloudCount -is [int]) {'Green'} else {'Red'})

if (($localCount -is [int]) -and ($cloudCount -is [int])) {
    if ($localCount -eq $cloudCount) {
        Write-Host ""
        Write-Host "  WARNING: Both sides return $localCount articles." -ForegroundColor Yellow
        Write-Host "  This usually means localhost:8000 still talks to a cloud DB," -ForegroundColor Yellow
        Write-Host "  or NEXT_PUBLIC_API_URL on local Next.js still points to the cloud." -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "  OK: environments are isolated (different article counts)." -ForegroundColor Green
    }
}

# ----------------------------------------------------------------------
Write-Section "5. Front-end build-time API target"
$slugPage = Join-Path $repo 'parent-website\app\articles\[slug]\page.tsx'
if (Test-Path $slugPage) {
    $hardcoded = Select-String -Path $slugPage -Pattern "drsscribe\.com|localhost:8000" -ErrorAction SilentlyContinue
    if ($hardcoded) {
        Write-Host "  Hardcoded URLs found in $slugPage :" -ForegroundColor Yellow
        $hardcoded | ForEach-Object { Write-Host ("    line {0}: {1}" -f $_.LineNumber, $_.Line.Trim()) -ForegroundColor DarkYellow }
    }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
Write-Host ""
