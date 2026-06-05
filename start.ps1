$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Demarrage Ink & Fate..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Write-Host 'Backend' -ForegroundColor Green; cd '$root\backend'; uvicorn api_main:app --reload --port 8000"

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Write-Host 'Frontend' -ForegroundColor Blue; cd '$root\frontend'; npm run dev"

Write-Host ""
Write-Host "Backend  -> http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend -> http://localhost:5173" -ForegroundColor Blue
Write-Host "Docs API -> http://localhost:8000/docs" -ForegroundColor Yellow
