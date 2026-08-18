# NAIC EU — volledig pakket naar P:\Jules\Apps\NAIC
$ErrorActionPreference = "Stop"

$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DestRoot = "P:\Jules\Apps\NAIC"
$Tgz = "$env:TEMP\naic-eu-complete-src.tgz"

$ExpectedB64Len = 390992
$ExpectedSha256 = "06af451957bf8e54d957829f9ce70ef42eaf5bd76332870da9fa03e66bb9ad6c"

$b64 = (1..8 | ForEach-Object { Get-Content (Join-Path $Dir "part$_.b64") -Raw }) -join ""
$b64 = $b64.Trim()
if ($b64.Length -ne $ExpectedB64Len) {
    throw "Base64 lengte $($b64.Length), verwacht $ExpectedB64Len"
}

$bytes = [Convert]::FromBase64String($b64)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = ([BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', '').ToLower()
if ($hash -ne $ExpectedSha256) {
    throw "SHA256 mismatch"
}

[IO.Directory]::CreateDirectory($DestRoot) | Out-Null
[IO.File]::WriteAllBytes($Tgz, $bytes)
Push-Location $DestRoot
try { tar -xzf $Tgz } finally { Pop-Location }
Remove-Item $Tgz -Force -ErrorAction SilentlyContinue

Write-Host "==> Klaar: $DestRoot"
Write-Host "    Zie LOCAL-FIRST.md voor lokaal verder werken."
