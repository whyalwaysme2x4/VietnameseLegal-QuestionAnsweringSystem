$ErrorActionPreference = 'Stop'
$pidPath = Join-Path $PSScriptRoot 'server.pid'
if (-not (Test-Path -LiteralPath $pidPath)) { Write-Output 'No demo PID file.'; exit }
$demoPid = [int](Get-Content -LiteralPath $pidPath)
$process = Get-CimInstance Win32_Process -Filter "ProcessId = $demoPid"
$expected = @((Join-Path $PSScriptRoot '.venv\Scripts\python.exe'), (Join-Path $PSScriptRoot '.venv-gpu\Scripts\python.exe'))
if ($process -and $process.ExecutablePath -in $expected -and $process.CommandLine -match 'app\.py') {
    # Windows venv python.exe can launch a base-python child. Stop this verified
    # process tree so the model process does not keep the port and RAM alive.
    & taskkill.exe /PID $demoPid /T /F | Out-Null
    Write-Output "Stopped W1-W5 demo PID $demoPid"
} elseif ($process) { throw 'PID does not match this demo. Nothing stopped.' }
