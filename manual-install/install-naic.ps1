# NAIC handmatige installatie -> P:\Jules\Apps\NAIC
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dest = "P:\Jules\Apps\NAIC"
$Zip = "$env:TEMP\naic-eu-local.zip"
$Temp = "$env:TEMP\naic-eu-extract"

$b64 = (1..4 | ForEach-Object { Get-Content (Join-Path $Dir "part$_.b64") -Raw }) -join ""
if ($b64.Trim().Length -ne 37760) {
    throw "Base64 lengte $($b64.Trim().Length), verwacht 37760"
}

[IO.Directory]::CreateDirectory($Dest) | Out-Null
[IO.File]::WriteAllBytes($Zip, [Convert]::FromBase64String($b64.Trim()))

if (Test-Path $Temp) { Remove-Item $Temp -Recurse -Force }
New-Item -ItemType Directory -Path $Temp | Out-Null
[System.IO.Compression.ZipFile]::ExtractToDirectory($Zip, $Temp)
Copy-Item -Path "$Temp\*" -Destination $Dest -Recurse -Force

Remove-Item $Zip -Force -ErrorAction SilentlyContinue
Remove-Item $Temp -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "==> Klaar: $Dest"
Write-Host "==> Volgende stappen:"
Write-Host "    cd $Dest"
Write-Host "    python -m venv .venv"
Write-Host "    .venv\Scripts\activate"
Write-Host "    pip install -e ."
