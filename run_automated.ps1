# run_automated.ps1
# Continuous execution loop for Cartoon Agent
# Runs every 12 hours (43200 seconds) to stay within YouTube API free tier limits (10,000 units/day).

$IntervalSeconds = 43200 # 12 hours
$LogFile = "e:\Antigravity\automated_run.log"

Write-Host "🤖 Cartoon Agent Automation Loop Started" -ForegroundColor Green
Write-Host "📅 Interval: Every 12 hours (2 runs/day)"
Write-Host "📝 Logging to: $LogFile"
Write-Host "❌ Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Starting run..." -ForegroundColor Cyan
    
    try {
        # Activate venv and run
        & "e:\Antigravity\.venv\Scripts\Activate.ps1"
        $env:PYTHONIOENCODING='utf-8'
        
        # Run main.py and capture output to log + console
        python e:\Antigravity\main.py 2>&1 | Tee-Object -FilePath $LogFile -Append
    } catch {
        Write-Host "❌ Error during run: $_" -ForegroundColor Red
        "[$timestamp] ERROR: $_" | Out-File -FilePath $LogFile -Append
    }

    $nextRun = (Get-Date).AddSeconds($IntervalSeconds)
    Write-Host "✅ Run finished. Sleeping for 12 hours..." -ForegroundColor Green
    Write-Host "⏰ Next run scheduled for: $nextRun" -ForegroundColor Yellow
    Write-Host "----------------------------------------"
    
    Start-Sleep -Seconds $IntervalSeconds
}
