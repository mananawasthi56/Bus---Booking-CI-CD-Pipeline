
param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

Write-Host "WARNING: Current database will be replaced!" -ForegroundColor Yellow
$confirmation = Read-Host "Type RESTORE to continue"

if ($confirmation -ne "RESTORE") {
    Write-Host "Restore cancelled."
    exit 0
}

Write-Host "Copying backup into PostgreSQL container..."

docker compose cp $BackupFile db:/tmp/restore.dump

if ($LASTEXITCODE -ne 0) {
    throw "Failed to copy backup."
}

Write-Host "Restoring database..."

docker compose exec -T db pg_restore `
    -U busgo `
    -d busbooking `
    --clean `
    --if-exists `
    --no-owner `
    --no-acl `
    /tmp/restore.dump

if ($LASTEXITCODE -ne 0) {
    throw "Database restore failed. Check PostgreSQL logs."
}

docker compose exec -T db rm -f /tmp/restore.dump

Write-Host "Database restore completed!" -ForegroundColor Green
