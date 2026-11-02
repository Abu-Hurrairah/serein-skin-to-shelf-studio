$ErrorActionPreference = 'Stop'
$destination = Join-Path $PSScriptRoot '.env'
Write-Host 'Enter your official YouCam API Bearer key (input is hidden):'
$secure = Read-Host 'YouCam API key' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try { $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr).Trim() }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
if ([string]::IsNullOrWhiteSpace($token) -or $token.Length -lt 10 -or $token.Contains("`n")) {
  throw 'Key was empty or invalid. Nothing changed.'
}
$existing = @()
if (Test-Path $destination) {
  $existing = @(Get-Content -LiteralPath $destination | Where-Object {$_ -notmatch '^\s*YOUCAM_API_KEY\s*='})
}
$existing += 'YOUCAM_API_KEY=' + $token
[IO.File]::WriteAllLines($destination, [string[]]$existing, [Text.UTF8Encoding]::new($false))
$token = $null
Write-Host 'Saved to local .env only. This does NOT validate the key.'
Write-Host 'Never upload .env to GitHub or Devpost.'
