# ==============================================================================
# POWER HOUSE - Safe Launch Script (PowerShell)
# Launches Backend (FastAPI on :8000) and Frontend (Vite on :5173)
# Implements Port Protection, Health Verification & Non-Destructive Startup
# ==============================================================================

$RootPath = $PSScriptRoot
$BackendPath = Join-Path $RootPath "backend"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Starting POWER HOUSE Compliance Operating System" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# Helper Function: Inspect Port Status & Service Health
# ------------------------------------------------------------------------------
function Check-PortStatus {
    param (
        [int]$Port,
        [string]$HealthUrl,
        [string]$ExpectedService
    )

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        return @{
            Status        = "Free"
            Pid           = $null
            ProcessName   = $null
            IsPowerHouse  = $false
            IsHealthy     = $false
        }
    }

    $owningPids = @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
    $targetPid = $owningPids[0]
    $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    $procName = if ($proc) { $proc.ProcessName } else { "Unknown" }

    # Health Check via HTTP
    $isHealthy = $false
    $healthData = $null
    if ($HealthUrl) {
        try {
            $resp = Invoke-RestMethod -Uri $HealthUrl -Method Get -TimeoutSec 2 -ErrorAction Stop
            if ($ExpectedService -and $resp.service -eq $ExpectedService) {
                $isHealthy = $true
                $healthData = $resp
            } elseif (-not $ExpectedService -and $resp) {
                $isHealthy = $true
            }
        } catch {
            $isHealthy = $false
        }
    }

    # Identify if process belongs to POWER HOUSE / Uvicorn / Node
    $isPowerHouse = $false
    if ($isHealthy) {
        $isPowerHouse = $true
    } else {
        $cmdLine = ""
        try {
            $cim = Get-CimInstance Win32_Process -Filter "ProcessId = $targetPid" -ErrorAction SilentlyContinue
            $cmdLine = if ($cim) { $cim.CommandLine } else { "" }
        } catch {}

        if ($procName -match "python|uvicorn" -or $cmdLine -match "app\.main|powerhouse|uvicorn") {
            $isPowerHouse = $true
        }
    }

    return @{
        Status        = "Occupied"
        Pid           = $targetPid
        AllPids       = $owningPids
        ProcessName   = $procName
        IsPowerHouse  = $isPowerHouse
        IsHealthy     = $isHealthy
        HealthData    = $healthData
    }
}

# ------------------------------------------------------------------------------
# 1. Inspect Backend Port 8000
# ------------------------------------------------------------------------------
$backendCheck = Check-PortStatus -Port 8000 -HealthUrl "http://127.0.0.1:8000/health" -ExpectedService "power-house-api"

$launchBackend = $true

if ($backendCheck.Status -eq "Occupied") {
    if ($backendCheck.IsHealthy) {
        Write-Host "[OK] Healthy POWER HOUSE Backend detected on http://127.0.0.1:8000 (PID: $($backendCheck.Pid)). Reusing existing instance." -ForegroundColor Green
        $launchBackend = $false
    } elseif ($backendCheck.IsPowerHouse) {
        Write-Host "[!] Stale/unresponsive POWER HOUSE backend detected on port 8000 (PID: $($backendCheck.Pid)). Safely stopping stale process..." -ForegroundColor Yellow
        Stop-Process -Id $backendCheck.Pid -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        $launchBackend = $true
    } else {
        Write-Host "==================================================" -ForegroundColor Red
        Write-Host "  PORT 8000 CONFLICT - UNRELATED PROCESS DETECTED" -ForegroundColor Red
        Write-Host "==================================================" -ForegroundColor Red
        Write-Host "Port 8000 is occupied by an unrelated application:" -ForegroundColor Yellow
        Write-Host "  PID:          $($backendCheck.Pid)" -ForegroundColor Yellow
        Write-Host "  Process Name: $($backendCheck.ProcessName)" -ForegroundColor Yellow
        Write-Host "  Health Check: No response from POWER HOUSE /health endpoint" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To protect other software, automatic termination was NOT performed." -ForegroundColor Yellow
        Write-Host "Please stop the conflicting process or free port 8000 before proceeding." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

# ------------------------------------------------------------------------------
# 2. Inspect Frontend Port 5173
# ------------------------------------------------------------------------------
$frontendCheck = Check-PortStatus -Port 5173 -HealthUrl "http://localhost:5173" -ExpectedService ""

$launchFrontend = $true

if ($frontendCheck.Status -eq "Occupied") {
    if ($frontendCheck.IsHealthy) {
        Write-Host "[OK] Active Frontend detected on http://localhost:5173 (PID: $($frontendCheck.Pid)). Reusing existing instance." -ForegroundColor Green
        $launchFrontend = $false
    } else {
        if ($frontendCheck.ProcessName -match "node|vite") {
            Write-Host "[!] Stale frontend process detected on port 5173 (PID: $($frontendCheck.Pid)). Safely stopping it..." -ForegroundColor Yellow
            Stop-Process -Id $frontendCheck.Pid -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            $launchFrontend = $true
        } else {
            Write-Host "[!] Warning: Port 5173 is occupied by $($frontendCheck.ProcessName) (PID: $($frontendCheck.Pid))." -ForegroundColor Yellow
            $launchFrontend = $false
        }
    }
}

# ------------------------------------------------------------------------------
# 3. Launch Services
# ------------------------------------------------------------------------------
if ($launchBackend) {
    Write-Host ""
    Write-Host "[1/2] Starting Backend API on http://127.0.0.1:8000 ..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$BackendPath'; Write-Host 'POWER HOUSE Backend running at http://127.0.0.1:8000' -ForegroundColor Green; .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload"
    
    # Wait up to 5 seconds for backend to become healthy
    $attempts = 0
    while ($attempts -lt 10) {
        Start-Sleep -Milliseconds 500
        try {
            $h = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 1 -ErrorAction Stop
            if ($h.status -eq "healthy") {
                Write-Host "  -> Backend API verified healthy (200 OK)" -ForegroundColor Green
                break
            }
        } catch {}
        $attempts++
    }
} else {
    Write-Host ""
    Write-Host "[1/2] Backend API is already running at http://127.0.0.1:8000" -ForegroundColor Green
}

if ($launchFrontend) {
    Write-Host "[2/2] Starting Frontend UI on http://localhost:5173 ..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootPath'; Write-Host 'POWER HOUSE Frontend running at http://localhost:5173' -ForegroundColor Cyan; npm run dev"
} else {
    Write-Host "[2/2] Frontend UI is already running at http://localhost:5173" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  POWER HOUSE Services Ready" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "-> App URL:    http://localhost:5173" -ForegroundColor Yellow
Write-Host "-> API Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "-> Demo User:  mohith.enterprise@powerhouse.in" -ForegroundColor Yellow
Write-Host "-> Password:   Compliance2026!" -ForegroundColor Yellow
Write-Host ""
