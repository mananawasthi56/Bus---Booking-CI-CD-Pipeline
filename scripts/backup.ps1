
$ErrorActionPreference = "Stop"

# Create backup directory
$backupDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Generate timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $backupDir "busbooking_$timestamp.dump"

Write-Host "Starting PostgreSQL backup..." -ForegroundColor Cyan

# Create database backup inside PostgreSQL container
docker compose exec -T db pg_dump -U busgo -d busbooking -Fc -f /tmp/busbooking.dump

if ($LASTEXITCODE -ne 0) {
    throw "Database backup failed!"
}

# Copy backup from container to local machine
docker compose cp db:/tmp/busbooking.dump $backupFile

if ($LASTEXITCODE -ne 0) {
    throw "Failed to copy backup file!"
}

# Remove temporary container backup
docker compose exec -T db rm -f /tmp/busbooking.dump

Write-Host "Backup completed successfully!" -ForegroundColor Green
Write-Host "Backup location: $backupFile"
