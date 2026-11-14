
# 🚌 BusGo – Bus Booking Platform | DevOps & CI/CD Project

A containerized Bus Booking Platform built using FastAPI and PostgreSQL, with automated testing, Docker image publishing, health monitoring, database backup and restore, and Docker image rollback.

## 1. Project Overview

BusGo is a bus trip and seat reservation platform developed as part of a DevOps and Cloud Engineering assessment.

The project demonstrates how an application can be developed, containerized, tested, monitored, and maintained using modern DevOps practices.

### Main Objectives

- Build a functional bus booking backend.
- Containerize the application using Docker.
- Manage application and database services using Docker Compose.
- Automate testing through GitHub Actions.
- Build and publish Docker images to Docker Hub.
- Implement PostgreSQL backup and restore procedures.
- Implement Docker image versioning and rollback.
- Add application health checks and operational documentation.

## 2. Technology Stack

| Category | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL 18 |
| ORM | SQLAlchemy |
| API Documentation | Swagger / OpenAPI |
| Containerization | Docker |
| Container Orchestration | Docker Compose |
| CI/CD | GitHub Actions |
| Container Registry | Docker Hub |
| Testing | Pytest |
| Version Control | Git and GitHub |
| Operating Environment | Windows / Docker Desktop |

## 3. Architecture

```text
                Developer
                    |
                    v
                GitHub
                    |
                    v
             GitHub Actions
                    |
             +------+------+
             |             |
          Run Tests    Docker Build
             |             |
             |             v
             |         Docker Hub
             |             |
             +-------------+
                           |
                           v
                    Docker Compose
                           |
                  +--------+--------+
                  |                 |
                  v                 v
             FastAPI Backend   PostgreSQL 18
                  |                 |
                  +--------+--------+
                           |
                     Persistent Volume
```

## 4. Project Features

### Backend API

- User authentication.
- Bus management.
- Trip management.
- Seat availability.
- Seat booking and cancellation.
- Booking management.
- Dashboard endpoints.
- Admin-protected management operations.

### API Documentation

Once the backend is running:

- Swagger UI: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health
- API information: http://localhost:8000/api/v1

## 5. Docker Containerization

The application is containerized using a Dockerfile.

Implemented features:

- Python 3.11 slim base image.
- Dependency installation using requirements.txt.
- Non-root application user (`appuser`).
- Python output logging configuration.
- Docker image build and execution.
- Port 8000 exposed for the backend.

### Docker Compose

Docker Compose manages two services:

1. Backend – FastAPI application.
2. Database – PostgreSQL 18.

Implemented configurations:

- Service dependency management.
- PostgreSQL health check.
- Backend HTTP health check.
- Automatic container restart policy.
- Persistent PostgreSQL volume.
- Environment-based configuration.

### Run the Application

```powershell
docker compose up -d
```

### Check Containers

```powershell
docker compose ps
```

### Stop Containers

```powershell
docker compose stop
```

### View Logs

```powershell
docker compose logs --tail 50
```

## 6. CI/CD Pipeline – GitHub Actions

GitHub Actions automates the application testing and Docker image publishing process.

### Pipeline Workflow

1. Developer pushes code to GitHub.
2. GitHub Actions workflow is triggered.
3. Python environment is configured.
4. Dependencies are installed.
5. PostgreSQL service is started for tests.
6. Pytest executes the automated test suite.
7. If tests pass, Docker image build and publishing proceed.
8. Docker image is pushed to Docker Hub.

### Pipeline Jobs

**Job 1 – Run Tests**
- Python 3.11 environment.
- PostgreSQL service.
- Dependency installation.
- Automated Pytest execution.

**Job 2 – Build and Push Docker Image**
- Runs after successful tests.
- Docker Hub authentication using GitHub Secrets.
- Builds the Docker image.
- Publishes `latest` and Git commit SHA tags.

### GitHub Secrets

The workflow uses:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Credentials are stored in GitHub repository secrets rather than hardcoded into the workflow.

### Docker Hub Repository

https://hub.docker.com/r/mananawasthi/busgo-backend

Example image:

```powershell
docker pull mananawasthi/busgo-backend:latest
```

## 7. Image Versioning and Rollback

Docker images are published with:

- `latest` tag.
- Full Git commit SHA tag.

This allows specific application versions to be selected.

### Rollback Procedure

Set the desired previous image tag in `.env`:

```env
IMAGE_TAG=PREVIOUS_COMMIT_SHA
```

Pull and deploy the selected version:

```powershell
docker compose pull backend
docker compose up -d --no-build backend
```

### Verify Rollback

```powershell
docker compose ps
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

A rollback test was performed successfully using a previously published commit-specific Docker image.

## 8. Database Backup and Restore

PostgreSQL data is stored using a Docker named volume.

### Backup

Backup script:

```powershell
.\scripts\backup.ps1
```

The script:

1. Creates a timestamped backup filename.
2. Runs PostgreSQL `pg_dump`.
3. Uses custom archive format.
4. Copies the backup to the local backups directory.
5. Removes the temporary container backup.

Backup files are excluded from Git using `.gitignore`.

### Restore

A separate test database can be used to verify recovery without modifying the original database.

Create test database:

```powershell
docker compose exec db psql -U busgo -d postgres -c "CREATE DATABASE busbooking_restore_test;"
```

Copy backup into the container:

```powershell
docker compose cp .\backups\YOUR_BACKUP.dump db:/tmp/busbooking.dump
```

Restore:

```powershell
docker compose exec db pg_restore -U busgo -d busbooking_restore_test --no-owner --no-acl /tmp/busbooking.dump
```

Verify tables:

```powershell
docker compose exec db psql -U busgo -d busbooking_restore_test -c "\dt"
```

**Recovery verification status:** Database schema restoration was successfully tested for all four tables: users, buses, trips, and bookings. Actual record recovery remains unverified because the source database contained zero records during the test.

## 9. Health Monitoring and Observability

### Backend Health Check

Endpoint:

```text
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### Docker Health Checks

- PostgreSQL uses `pg_isready`.
- Backend uses an HTTP request to `/health`.
- Docker reports container health status.

### Monitoring Commands

Check service status:

```powershell
docker compose ps
```

Backend logs:

```powershell
docker compose logs backend --tail 100
```

Database logs:

```powershell
docker compose logs db --tail 100
```

Live logs:

```powershell
docker compose logs -f
```

Resource usage:

```powershell
docker stats
```

## 10. Security Improvements

Implemented:

- Non-root application user inside the backend container.
- Environment-based application configuration.
- GitHub Secrets for Docker Hub credentials.
- `.env` excluded from Git.
- Persistent database storage.
- Docker container restart policies.
- Health checks for application and database.

Note: Production secret rotation, TLS termination, and cloud deployment hardening remain future improvements.

## 11. Testing

Automated tests are executed using Pytest.

Test coverage includes:

- API home endpoint.
- Health endpoint.
- API information endpoint.
- Bus API.
- Successful booking.
- Duplicate seat booking.
- Invalid seat number.
- Booking cancellation.
- Rebooking a cancelled seat.
- Authenticated booking access.

Latest recorded local test result:

```text
11 passed
1 warning
```

GitHub Actions also completed successfully for the configured CI/CD workflow.

## 12. Repository Structure

```text
BusBooking-DevOps/
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── frontend/
│
├── scripts/
│   ├── backup.ps1
│   └── restore.ps1
│
├── tests/
│   ├── test_api.py
│   └── test_bookings.py
│
├── docs/
│   └── RUNBOOK.md
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

## 13. Operational Runbook

Operational procedures are documented in:

```text
docs/RUNBOOK.md
```

It covers:

- Application startup and shutdown.
- Container status.
- Health checks.
- Application and database logs.
- Backup procedures.
- Restore procedures.
- Image rollback.
- Troubleshooting.

## 14. Current Project Status

| Component | Status |
|---|---|
| Backend APIs | Implemented |
| PostgreSQL integration | Implemented |
| Automated tests | Passing |
| Dockerfile | Implemented |
| Docker Compose | Implemented |
| GitHub Actions CI | Successful |
| Docker Hub publishing | Successful |
| Image versioning | Implemented |
| Image rollback test | Successful |
| Database backup | Successful |
| Schema restore test | Successful |
| Backend health check | Healthy |
| Database health check | Healthy |
| Non-root Docker user | Verified |
| Operational Runbook | Created |
| Actual data recovery test | Pending |
| AWS deployment | Not implemented |

## 15. Future Scope

- AWS EC2 deployment.
- Nginx reverse proxy and HTTPS.
- Production secret management.
- Automated scheduled database backups.
- Actual populated-data recovery testing.
- Advanced metrics and monitoring dashboards.
- Automated deployment to a production server.

## 16. Author

**Project:** BusGo – Bus Booking Platform  
**Domain:** DevOps and Cloud Engineering  
**Repository:** https://github.com/mananawasthi56/Bus---Booking-CI-CD-Pipeline  
**Docker Hub:** https://hub.docker.com/r/mananawasthi/busgo-backend

---

This project demonstrates the practical implementation of containerization, CI automation, Docker image publishing, backup and restore procedures, rollback, security hardening, and operational monitoring.
