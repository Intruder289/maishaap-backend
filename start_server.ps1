# Script to safely start Django server on port 8001
# This script checks for existing processes and kills them first

param(
    [int]$Port = 8001
)

Write-Host "Starting Django server on port $Port..." -ForegroundColor Cyan
Write-Host ""

# Check if port is in use
$connections = netstat -ano | Select-String ":$Port.*LISTENING"

if ($connections) {
    Write-Host "Port $Port is already in use!" -ForegroundColor Red
    Write-Host "Killing existing processes..." -ForegroundColor Yellow
    
    foreach ($conn in $connections) {
        $processId = ($conn -split '\s+')[-1]
        if ($processId -and $processId -match '^\d+$') {
            try {
                $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($proc -and $proc.ProcessName -eq "python") {
                    Write-Host "  Killing PID $processId..." -ForegroundColor Yellow
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Milliseconds 500
                }
            } catch {
                Write-Host "  Could not kill PID $processId" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
    Write-Host "Waiting 2 seconds for ports to be released..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

# Verify port is free
$connections = netstat -ano | Select-String ":$Port.*LISTENING"
if ($connections) {
    Write-Host "ERROR: Port $Port is still in use. Please manually kill the processes." -ForegroundColor Red
    Write-Host "Run: .\check_ports.ps1 to see what's using the port" -ForegroundColor Yellow
    exit 1
}

Write-Host "Port $Port is free. Starting Django server..." -ForegroundColor Green
Write-Host ""

# Start Django server
python manage.py runserver $Port

