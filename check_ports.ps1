# Script to check and kill processes using ports 8000 and 8001

Write-Host "Checking processes on ports 8000 and 8001..." -ForegroundColor Yellow
Write-Host ""

# Get all processes listening on ports 8000 and 8001
$ports = @(8000, 8001)
$processes = @()

foreach ($port in $ports) {
    Write-Host "Port $port :" -ForegroundColor Cyan
    $connections = netstat -ano | Select-String ":$port.*LISTENING"
    
    if ($connections) {
        foreach ($conn in $connections) {
            $processId = ($conn -split '\s+')[-1]
            if ($processId -and $processId -match '^\d+$') {
                try {
                    $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
                    if ($proc) {
                        Write-Host "  PID: $processId - $($proc.ProcessName) - $($proc.Path)" -ForegroundColor Red
                        $processes += $proc
                    }
                } catch {
                    Write-Host "  PID: $processId - Process not found (may have terminated)" -ForegroundColor Gray
                }
            }
        }
    } else {
        Write-Host "  No processes found" -ForegroundColor Green
    }
    Write-Host ""
}

if ($processes.Count -gt 0) {
    Write-Host "Found $($processes.Count) Python/Django processes using these ports!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To kill all these processes, run:" -ForegroundColor Yellow
    Write-Host "  .\kill_port_processes.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or manually kill them with:" -ForegroundColor Yellow
    foreach ($proc in $processes) {
        Write-Host "  Stop-Process -Id $($proc.Id) -Force" -ForegroundColor White
    }
} else {
    Write-Host "No processes found on ports 8000 and 8001. Ports are free!" -ForegroundColor Green
}

