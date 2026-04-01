$TaskName = "AI_Workflow_Orchestrator"
$VbsPath = "$PSScriptRoot\run_background.vbs"

$Description = "Starts the AI Workflow Orchestrator in the background on logon."

$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsPath`""

$Trigger = New-ScheduledTaskTrigger -AtLogOn

$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 365)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description $Description

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AI Workflow Orchestrator Startup Task Installed!" -ForegroundColor Green
Write-Host "Task Name: $TaskName"
Write-Host "Launcher: $VbsPath"
Write-Host "============================================================" -ForegroundColor Cyan
