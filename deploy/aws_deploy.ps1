<#
  ALI TRAVEL - deploy "agent" for an AWS server (Ubuntu or Amazon Linux).

  What it does, in order:
    1. finds the key file (default: ~\.ssh\zuhriddin.pem) and the right login name (ubuntu, ec2-user, admin or root);
    2. builds the website (npm run build) when Node.js is installed, otherwise uses the existing frontend\dist;
    3. packs the project (code, built website, photos and, the first time, your database) and your settings (.env);
    4. connects with ssh, installs Python/nginx/certbot, starts the website and the Telegram bot as services, and sets up HTTPS when a domain is given;
    5. checks that the site answers.
  Run it again later to update the server: the live database and the server's SECRET_KEY are never overwritten (unless you ask).

  Examples (PowerShell, from the project folder):
    .\deploy\aws_deploy.ps1 -ServerHost 3.120.45.67
    .\deploy\aws_deploy.ps1 -ServerHost 3.120.45.67 -Domain alitravel.uz -Email alitravel004@gmail.com
    .\deploy\aws_deploy.ps1 -ServerHost 3.120.45.67 -DryRun        (packs everything but does not connect)

  The AWS security group must allow inbound TCP 22 (ssh), 80 (http) and 443 (https).
  The private key is only handed to ssh; this script never prints or copies it.
#>
[CmdletBinding()]
param(
  [string]$ServerHost,
  [string]$User,
  [string]$Key = (Join-Path $HOME '.ssh\zuhriddin.pem'),
  [string]$Domain = '',
  [string]$Email = '',
  [switch]$NoData,        # do not send the local database and photos; the server loads the sample data instead
  [switch]$ReplaceData,   # overwrite the server's database with the local one (a backup is kept on the server)
  [switch]$SkipBuild,     # do not run npm run build
  [switch]$DryRun         # pack everything, show the plan, do not connect
)

$ErrorActionPreference = 'Continue'   # native commands write progress to stderr; failures are checked through exit codes
$Root = Split-Path -Parent $PSScriptRoot
$Work = Join-Path $env:TEMP ('alitravel-deploy-' + [guid]::NewGuid().ToString('N').Substring(0, 8))

function Step($text) { Write-Host ''; Write-Host "==> $text" -ForegroundColor Cyan }
function Warn($text) { Write-Host "!!  $text" -ForegroundColor Yellow }
function Fail($text) { Write-Host "XX  $text" -ForegroundColor Red; Cleanup; exit 1 }
function Cleanup { if (Test-Path $Work) { Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue } }

$SshOptions = @('-i', $Key, '-o', 'StrictHostKeyChecking=accept-new', '-o', 'ServerAliveInterval=30', '-o', 'ConnectTimeout=20')

function Invoke-Remote([string]$Command, [switch]$Quiet) {
  $lines = & ssh @SshOptions "$User@$ServerHost" $Command 2>&1 | ForEach-Object { "$_" }
  $code = $LASTEXITCODE
  if (-not $Quiet) { $lines | ForEach-Object { Write-Host $_ } }
  return @{ Code = $code; Output = $lines }
}

function Send-File([string]$Local, [string]$Remote) {
  & scp @SshOptions $Local "${User}@${ServerHost}:$Remote" 2>&1 | ForEach-Object { "$_" } | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "Could not upload $(Split-Path -Leaf $Local)." }
}

# ---------------------------------------------------------------- 0. checks
Step 'Checking this computer'
foreach ($tool in 'ssh', 'scp', 'tar') { if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { Fail "'$tool' was not found. Install the Windows feature 'OpenSSH Client' (Settings > Apps > Optional features)." } }
if (-not (Test-Path (Join-Path $Root 'backend\manage.py'))) { Fail "This script must stay in the project's deploy folder (backend\manage.py not found in $Root)." }
if (-not (Test-Path $Key)) { Fail "The key file was not found: $Key  (use -Key to point at it)." }
if (-not $ServerHost) { $ServerHost = Read-Host 'The server address (public IPv4 address or DNS name from the AWS console)' }
if (-not $ServerHost) { Fail 'No server address given.' }
$Domain = $Domain.Trim().ToLower() -replace '^https?://', '' -replace '^www\.', '' -replace '/.*$', ''
New-Item -ItemType Directory -Force -Path $Work | Out-Null

# ssh refuses a key that other Windows users can read: give the file to the current user only (this changes permissions, not the key)
function Protect-Key {
  & icacls $Key /inheritance:r | Out-Null
  & icacls $Key /grant:r "$($env:USERNAME):(R)" | Out-Null
}

# ---------------------------------------------------------------- 1. the website build
Step 'The website files'
$dist = Join-Path $Root 'frontend\dist\index.html'
if (-not $SkipBuild -and (Get-Command npm -ErrorAction SilentlyContinue)) {
  Push-Location (Join-Path $Root 'frontend')
  if (-not (Test-Path 'node_modules')) { & npm install --no-audit --no-fund 2>&1 | ForEach-Object { "$_" } | Out-Null }
  & npm run build 2>&1 | ForEach-Object { "$_" } | Select-Object -Last 3 | ForEach-Object { Write-Host $_ }
  $built = ($LASTEXITCODE -eq 0)
  Pop-Location
  if (-not $built) { Fail 'npm run build failed.' }
} elseif (Test-Path $dist) {
  Warn 'Using the website already built in frontend\dist (npm was not used).'
} else {
  Fail 'There is no built website: install Node.js and run again, or run  npm run build  in the frontend folder.'
}

# ---------------------------------------------------------------- 2. the settings (.env) for the server
Step 'The settings for the server'
$address = if ($Domain) { $Domain } else { $ServerHost }
$scheme = if ($Domain) { 'https' } else { 'http' }
$hosts = @($address, '127.0.0.1', 'localhost')
if ($Domain) { $hosts = @($Domain, "www.$Domain", $ServerHost, '127.0.0.1', 'localhost') }
$origins = if ($Domain) { "https://$Domain,https://www.$Domain,http://$ServerHost" } else { "http://$ServerHost" }
$overridden = 'DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS', 'SITE_URL', 'CORS_ORIGINS', 'CSRF_TRUSTED_ORIGINS', 'NUM_PROXIES', 'SERVE_FRONTEND', 'SECURE_SSL_REDIRECT', 'SECURE_HSTS_SECONDS', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'
$envLines = @('# Made by deploy\aws_deploy.ps1', 'DEBUG=false', 'SECRET_KEY=__made_on_the_server__', "ALLOWED_HOSTS=$($hosts -join ',')", "SITE_URL=${scheme}://$address",
              "CORS_ORIGINS=$origins", "CSRF_TRUSTED_ORIGINS=$origins", 'NUM_PROXIES=1', 'SERVE_FRONTEND=false', 'SECURE_SSL_REDIRECT=false', 'SECURE_HSTS_SECONDS=0')
$kept = @()
$localEnv = Join-Path $Root 'backend\.env'
if (Test-Path $localEnv) {
  foreach ($line in Get-Content $localEnv) {
    if ($line -match '^\s*([A-Z0-9_]+)\s*=(.*)$' -and $overridden -notcontains $Matches[1] -and $Matches[2].Trim() -ne '') { $envLines += $line.Trim(); $kept += $Matches[1] }
  }
}
Write-Host ("Carried over from your local .env: " + ($(if ($kept) { $kept -join ', ' } else { 'nothing' })))
$envFile = Join-Path $Work 'alitravel.env'
[IO.File]::WriteAllText($envFile, (($envLines -join "`n") + "`n"), (New-Object Text.UTF8Encoding($false)))
if ($kept -contains 'TELEGRAM_BOT_TOKEN') { Warn 'The Telegram bot will run on the server: stop the bot on your own computer (two copies cannot poll the same bot).' }

# ---------------------------------------------------------------- 3. the package
Step 'Packing the project'
$package = Join-Path $Work 'package.tgz'
$exclude = @('--exclude=__pycache__', '--exclude=*.pyc', '--exclude=backend/.env', '--exclude=backend/venv', '--exclude=backend/backups', '--exclude=backend/staticfiles', '--exclude=backend/*.log')
if ($NoData) { $exclude += '--exclude=backend/db.sqlite3'; $exclude += '--exclude=backend/media' }
# Windows' own tar understands C:\ paths; Git's GNU tar (often first on PATH) reads "C:" as a remote host
$tar = Join-Path $env:SystemRoot 'System32\tar.exe'
if (-not (Test-Path $tar)) { $tar = 'tar' }
& $tar -czf $package -C $Root @exclude backend frontend/dist deploy 2>&1 | ForEach-Object { "$_" } | Out-Null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $package)) { Fail 'Packing failed.' }
$serverScript = Join-Path $Work 'server_setup.sh'
[IO.File]::WriteAllText($serverScript, ((Get-Content (Join-Path $PSScriptRoot 'server_setup.sh') -Raw) -replace "`r`n", "`n"), (New-Object Text.UTF8Encoding($false)))
Write-Host ("Package: {0:N1} MB  (database and photos: {1})" -f ((Get-Item $package).Length / 1MB), $(if ($NoData) { 'not sent' } else { 'sent' }))

if ($DryRun) {
  Step 'Dry run: nothing was sent'
  Write-Host "Would connect to $ServerHost with $Key, login names tried: $(if ($User) { $User } else { 'ubuntu, ec2-user, admin, root' })."
  Write-Host "The site would answer at ${scheme}://$address  (domain: $(if ($Domain) { $Domain } else { 'none, plain http by address' }))."
  Cleanup; exit 0
}

# ---------------------------------------------------------------- 4. connect
Step "Connecting to $ServerHost"
$candidates = if ($User) { @($User) } else { @('ubuntu', 'ec2-user', 'admin', 'root') }
$User = ''
$permissionsFixed = $false
foreach ($name in $candidates) {
  $test = & ssh @SshOptions -o BatchMode=yes "$name@$ServerHost" 'echo connected' 2>&1 | ForEach-Object { "$_" }
  if ($test -match 'UNPROTECTED PRIVATE KEY|bad permissions' -and -not $permissionsFixed) {
    Warn 'ssh does not accept the key file permissions: restricting the file to your Windows user.'
    Protect-Key; $permissionsFixed = $true
    $test = & ssh @SshOptions -o BatchMode=yes "$name@$ServerHost" 'echo connected' 2>&1 | ForEach-Object { "$_" }
  }
  if ($test -match 'connected') { $User = $name; break }
  if ($test -match 'timed out|Connection refused|No route|Could not resolve') { Fail "Cannot reach $ServerHost ($($test -join ' ')). Check the address and that the AWS security group allows port 22." }
}
if (-not $User) { Fail 'The server did not accept the key for ubuntu, ec2-user, admin or root. Check the key pair of the instance (and pass -User if you use another login name).' }
Write-Host "Connected as $User."

# ---------------------------------------------------------------- 5. upload and install
Step 'Uploading'
$null = Invoke-Remote 'mkdir -p /tmp/alitravel' -Quiet
Send-File $package '/tmp/alitravel/package.tgz'
Send-File $envFile '/tmp/alitravel/alitravel.env'
Send-File $serverScript '/tmp/alitravel/server_setup.sh'

Step 'Installing and starting everything on the server (a few minutes the first time)'
$replace = if ($ReplaceData) { 1 } else { 0 }
$run = Invoke-Remote "sudo bash /tmp/alitravel/server_setup.sh /tmp/alitravel/package.tgz /tmp/alitravel/alitravel.env '$Domain' '$Email' $replace"
if ($run.Code -ne 0) { Fail "The setup on the server stopped with an error (code $($run.Code)). Read the lines above; run the script again after fixing it." }

# ---------------------------------------------------------------- 6. check from here
Step 'Checking the site from this computer'
try {
  # with a domain, nginx answers only to that name (and redirects to https)
  $answer = Invoke-WebRequest -UseBasicParsing -TimeoutSec 20 -Uri "${scheme}://$address/api/site-content/"
  Write-Host "The API answered: HTTP $($answer.StatusCode)" -ForegroundColor Green
} catch {
  Warn "The server did not answer from outside. Open the AWS security group of the instance and allow inbound TCP 80 and 443 (and 22) from anywhere."
}
Write-Host ''
Write-Host "Your site: ${scheme}://$address" -ForegroundColor Green
if ($Domain) { Write-Host "The domain's DNS 'A' records for $Domain and www.$Domain must point to $ServerHost." }
Write-Host 'Logs on the server:  sudo journalctl -u alitravel -f    and    sudo journalctl -u alitravel-bot -f'
Write-Host 'Update later: change the project, then run this script again.'
Cleanup
