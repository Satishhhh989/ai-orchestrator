$ShortcutName = "AI_Workflow_Orchestrator.lnk"
$StartupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$VbsPath = "$PSScriptRoot\run_background.vbs"
$ShortcutPath = Join-Path $StartupFolder $ShortcutName

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$VbsPath`""
$Shortcut.WorkingDirectory = "$PSScriptRoot"
$Shortcut.Description = "Starts the AI Workflow Orchestrator in the background on logon."
$Shortcut.Save()

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AI Workflow Orchestrator Startup Shortcut Created!" -ForegroundColor Green
Write-Host "Location: $ShortcutPath"
Write-Host "============================================================" -ForegroundColor Cyan
