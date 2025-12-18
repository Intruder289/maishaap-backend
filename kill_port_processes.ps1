# Script to kill all processes using ports 8000 and 8001

Write-Host "Killing processes on ports 8000 and 8001..." -ForegroundColor Yellow
Write-Host ""

$ports = @(8000, 8001)
$killed = @()

foreach ($port in $ports) {
    Write-Host "Checking port $port..." -ForegroundColor Cyan
    $connections = netstat -ano | Select-String ":$port.*LISTENING"
    
    if ($connections) {
        foreach ($conn in $connections) {
            $processId = ($conn -split '\s+')[-1]
            if ($processId -and $processId -match '^\d+$') {
                try {
                    $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
                    if ($proc -and $proc.ProcessName -eq "python") {
                        Write-Host "  Killing PID $processId ($($proc.ProcessName))..." -ForegroundColor Red
                        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                        $killed += $processId
                        Start-Sleep -Milliseconds 500
                    }
                } catch {
                    Write-Host "  Could not kill PID $processId : $_" -ForegroundColor Yellow
                }
            }
        }
    }
}

Write-Host ""
if ($killed.Count -gt 0) {
    Write-Host "Successfully killed $($killed.Count) process(es): $($killed -join ', ')" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ports 8000 and 8001 should now be free!" -ForegroundColor Green
    Write-Host "You can now start your Django server with:" -ForegroundColor Yellow
    Write-Host "  python manage.py runserver 8001" -ForegroundColor White
} else {
    Write-Host "No Python processes found to kill." -ForegroundColor Green
}

