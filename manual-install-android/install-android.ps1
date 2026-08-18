# NAIC Android handmatige installatie -> P:\Jules\Apps\NAIC\naic-android
$ErrorActionPreference = "Stop"

$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DestRoot = "P:\Jules\Apps\NAIC"
$Tgz = "$env:TEMP\naic-android-src.tgz"

$ExpectedB64Len = 79232
$ExpectedSha256 = "29c0a89e90929bf6d0fdf1758a22a9a93aaf3edbec3eb062a5695c0900375c49"

$b64 = (1..4 | ForEach-Object { Get-Content (Join-Path $Dir "part$_.b64") -Raw }) -join ""
$b64 = $b64.Trim()
if ($b64.Length -ne $ExpectedB64Len) {
    throw "Base64 lengte $($b64.Length), verwacht $ExpectedB64Len. Controleer part1.b64 t/m part4.b64."
}

$bytes = [Convert]::FromBase64String($b64)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = ([BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', '').ToLower()
if ($hash -ne $ExpectedSha256) {
    throw "SHA256 $hash, verwacht $ExpectedSha256 — bestand corrupt."
}

[IO.Directory]::CreateDirectory($DestRoot) | Out-Null
[IO.File]::WriteAllBytes($Tgz, $bytes)

Push-Location $DestRoot
try {
    tar -xzf $Tgz
} finally {
    Pop-Location
}

Remove-Item $Tgz -Force -ErrorAction SilentlyContinue

Write-Host "==> Klaar: $DestRoot\naic-android"
Write-Host ""
Write-Host "==> APK bouwen (Android Studio of):"
Write-Host "    cd $DestRoot\naic-android"
Write-Host "    .\gradlew.bat assembleDebug"
Write-Host ""
Write-Host "==> APK staat daarna in:"
Write-Host "    $DestRoot\naic-android\app\build\outputs\apk\debug\app-debug.apk"
