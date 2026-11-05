$ErrorActionPreference = 'Stop'
$demoRoot = $PSScriptRoot
$listener = Get-NetTCPConnection -LocalPort 8086 -State Listen -ErrorAction SilentlyContinue
if ($listener) { throw 'Port 8086 is already in use. Check the existing process before starting this demo.' }
$pythonPath = Join-Path $demoRoot '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath (Join-Path $demoRoot 'runs\gpu_compatible.json')) {
    $pythonPath = Join-Path $demoRoot '.venv-gpu\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Missing .venv. Run setup steps in README.md first.' }
$process = Start-Process -FilePath $pythonPath -ArgumentList '-B','app.py' -WorkingDirectory $demoRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $demoRoot 'server.out.log') -RedirectStandardError (Join-Path $demoRoot 'server.err.log') -PassThru
$process.Id | Set-Content -LiteralPath (Join-Path $demoRoot 'server.pid')
Write-Output "W1-W6 demo PID $($process.Id): http://127.0.0.1:8086"
