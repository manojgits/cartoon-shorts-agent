$ErrorActionPreference = "Stop"

$taskName = "CartoonShortsAgent"
$pythonPath = "e:\Antigravity\.venv\Scripts\python.exe"
$scriptPath = "e:\Antigravity\main.py"
$workDir = "e:\Antigravity"

Write-Host "Creating Scheduled Task '$taskName' to run daily at 9:00 AM..."

# Unregister if it already exists
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing task."
}

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory $workDir
$trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName $taskName -Description "Runs the Cartoon Shorts Agent daily at 9 AM"

Write-Host "Scheduled task '$taskName' created successfully! It will now run automatically in the background every day at 9:00 AM."
