# Electron-App starten (oeffnet Tree + Viewer Fenster)
Start-Process "npm" -ArgumentList "start" -WorkingDirectory $PSScriptRoot

# Neues PowerShell-Fenster mit Claude Code YOLO im Projekt-Root
# Definiert die Funktion 'sub' zum Oeffnen weiterer Claude-Fenster
$initCommand = @"
cd '$PSScriptRoot'
function sub {
    Write-Host 'Oeffne Sub-Claude mit aktuellem Kontext...' -ForegroundColor Cyan
    Start-Process pwsh -ArgumentList '-NoExit','-Command',"cd '$(Get-Location)'; claude --dangerously-skip-permissions"
    Write-Host 'Sub-Claude geoeffnet. Kontext liegt in vault/.claude-context.md' -ForegroundColor Green
}
Write-Host '--- LeanHierarchy Claude Code ---' -ForegroundColor Cyan
Write-Host 'Kontext-Datei: vault/.claude-context.md (wird automatisch aktualisiert)' -ForegroundColor DarkGray
Write-Host 'Tipp: Markiere Woerter im Viewer, Kontext wird automatisch in die Zwischenablage kopiert.' -ForegroundColor DarkGray
Write-Host 'Funktion "sub" oeffnet ein weiteres Claude-Fenster fuer Detailfragen.' -ForegroundColor DarkGray
Write-Host ''
claude --dangerously-skip-permissions
"@

Start-Process "pwsh" -ArgumentList "-NoExit", "-Command", $initCommand
