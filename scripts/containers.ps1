<#
.SYNOPSIS
    MedScribe Docker Containers Manager
.DESCRIPTION
    Start (up) or stop (down) all Docker containers with proper dependency order.
.PARAMETER Action
    up   - Start all containers
    down - Stop all containers
    status - Show container status
.EXAMPLE
    .\scripts\containers.ps1 up
    .\scripts\containers.ps1 down
    .\scripts\containers.ps1 status
#>

param(
    [Parameter(Position=0)]
    [ValidateSet('up', 'down', 'status')]
    [string]$Action
)

$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

# ── Ensure Docker Desktop is running ──
function Ensure-Docker {
    $null = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n[!] Docker Desktop is not running. Starting it..." -ForegroundColor Yellow
        $dockerExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $dockerExe) {
            Start-Process $dockerExe
        } else {
            Write-Host "[ERROR] Docker Desktop not found at $dockerExe" -ForegroundColor Red
            exit 1
        }
        Write-Host "Waiting for Docker engine to be ready..." -ForegroundColor DarkGray
        $maxWait = 120  # seconds
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 3
            $waited += 3
            $null = docker info 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Docker is ready! (waited ${waited}s)" -ForegroundColor Green
                return
            }
            Write-Host "  ... still waiting (${waited}s)" -ForegroundColor DarkGray
        }
        Write-Host "[ERROR] Docker did not start within ${maxWait}s. Please start Docker Desktop manually." -ForegroundColor Red
        exit 1
    }
}

# Service groups in dependency order
$Infra    = @('postgres', 'redis', 'minio', 'meilisearch')
$Apps     = @('backend', 'celery-worker', 'frontend', 'parent-website')
$Proxy    = @('nginx')
$All      = $Infra + $Apps + $Proxy

function Show-Status {
    Write-Host "`n=== MedScribe Container Status ===" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
}

function Start-Containers {
    Write-Host "`n=== Starting MedScribe Containers ===" -ForegroundColor Green

    Write-Host "`n[1/3] Infrastructure (postgres, redis, minio, meilisearch)..." -ForegroundColor Yellow
    docker-compose up -d $Infra
    Write-Host "Waiting for health checks..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 5

    Write-Host "`n[2/3] Applications (backend, celery, frontend, parent-website)..." -ForegroundColor Yellow
    docker-compose up -d $Apps
    Start-Sleep -Seconds 3

    Write-Host "`n[3/3] Proxy (nginx)..." -ForegroundColor Yellow
    docker-compose up -d $Proxy

    Write-Host "`n=== All containers started ===" -ForegroundColor Green
    Show-Status
}

function Stop-Containers {
    Write-Host "`n=== Stopping MedScribe Containers ===" -ForegroundColor Red

    Write-Host "`n[1/3] Proxy..." -ForegroundColor Yellow
    docker-compose stop $Proxy

    Write-Host "`n[2/3] Applications..." -ForegroundColor Yellow
    docker-compose stop $Apps

    Write-Host "`n[3/3] Infrastructure..." -ForegroundColor Yellow
    docker-compose stop $Infra

    Write-Host "`n=== All containers stopped ===" -ForegroundColor Red
    Show-Status
}

if (-not $Action) {
    Write-Host "`nUsage:" -ForegroundColor Cyan
    Write-Host "  .\scripts\containers.ps1 up      # Start all containers"
    Write-Host "  .\scripts\containers.ps1 down    # Stop all containers"
    Write-Host "  .\scripts\containers.ps1 status  # Show status"
    Write-Host ""
    exit 0
}

Ensure-Docker

switch ($Action) {
    'up'     { Start-Containers }
    'down'   { Stop-Containers }
    'status' { Show-Status }
}
