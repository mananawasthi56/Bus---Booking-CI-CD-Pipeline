
# BusGo - Operations Runbook

## 1. Application Overview

BusGo is a bus booking platform built using FastAPI and PostgreSQL.

Services:
- Backend: FastAPI
- Database: PostgreSQL 18
- Container management: Docker Compose
- CI/CD: GitHub Actions
- Image registry: Docker Hub

## 2. Start Application

```powershell
docker compose up -d
```

## 3. Stop Application

```powershell
docker compose stop
```

## 4. Check Container Status

```powershell
docker compose ps
```

## 5. Check Application Health

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"healthy"}
```

## 6. View Backend Logs

```powershell
docker compose logs backend --tail 100
```

## 7. View Database Logs

```powershell
docker compose logs db --tail 100
```

## 8. Follow Live Logs

```powershell
docker compose logs -f
```

## 9. Restart Backend

```powershell
docker compose restart backend
```

## 10. Database Backup

```powershell
.\scripts\backup.ps1
```

## 11. Database Restore

Use the tested restore procedure and verify restored tables before considering recovery successful.

## 12. Docker Image Rollback

Change IMAGE_TAG in .env to the previous published SHA tag.

Then execute:

```powershell
docker compose pull backend
docker compose up -d --no-build backend
```

## 13. Verify Rollback

```powershell
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 14. Troubleshooting

### Backend restarting

```powershell
docker compose logs backend --tail 100
```

### Database unhealthy

```powershell
docker compose logs db --tail 100
```

### Rebuild backend

```powershell
docker compose build --no-cache backend
docker compose up -d
```

### Check Docker resources

```powershell
docker stats
```

## 15. Persistent Storage

PostgreSQL data is stored in the Docker named volume:

postgres_data

Do not use docker compose down -v during normal shutdown because it deletes the database volume.
