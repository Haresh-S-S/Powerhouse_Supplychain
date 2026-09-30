# POWER HOUSE Backend — FastAPI & PostgreSQL Foundation

Production-ready backend API and persistent data layer for **POWER HOUSE** — an intelligent enterprise compliance and regulatory approval management platform.

---

## 🏗️ Architecture

```
React + Vite Frontend (Port 5173)
        ↓  REST API (HTTP / JSON)
FastAPI Backend (Port 8000)
        ↓  Business Logic Services
Deterministic Business Analysis Engine (Python)
        ↓  SQLAlchemy ORM (v2.0)
PostgreSQL Database (with SQLite local fallback)
        ↓
Alembic Migrations
```

---

## 📦 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **ORM & Models**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/latest/)
- **Testing**: [Pytest](https://docs.pytest.org/) & `httpx` / `TestClient`
- **Database**: PostgreSQL (Default) / SQLite (Zero-config local dev)

---

## 🚀 Quickstart Guide

### 1. Create and Activate Virtual Environment

```powershell
# In the backend directory
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env`:

```powershell
cp .env.example .env
```

Default `.env` configuration:
```env
APP_NAME=POWER HOUSE Backend API
ENVIRONMENT=development
DEBUG=True
API_V1_STR=/api/v1
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/powerhouse
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

*(If PostgreSQL is not running locally, SQLite `sqlite:///./powerhouse.db` will be used automatically).*

### 4. Run Database Migrations

```powershell
alembic upgrade head
```

### 5. Seed Initial Data (Optional)

Populates the default **Powerhouse Industries** enterprise profile and runs baseline analysis:

```powershell
python scripts/seed_data.py
```

### 6. Start the Backend API Server

```powershell
uvicorn app.main:app --reload --port 8000
```

- **API Root**: `http://localhost:8000/`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc UI**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`

---

## 🧪 Running Automated Tests

Run the complete test suite with verbose reporting:

```powershell
pytest -v
```

Tests cover:
- Health endpoint validation
- Business Profile CRUD
- Business Analysis execution & persistence
- Approval rules & statutory conditions (Manufacturing, PF, ESI, IEC, etc.)
- Government scheme deterministic scoring

---

## 📡 REST API Reference (`/api/v1`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check |
| `POST` | `/api/v1/business-profile` | Create new business profile |
| `GET` | `/api/v1/business-profile` | List all business profiles |
| `GET` | `/api/v1/business-profile/{id}` | Get business profile by ID |
| `PUT` | `/api/v1/business-profile/{id}` | Update business profile |
| `POST` | `/api/v1/business-analysis/{profile_id}` | Execute business analysis & persist entities |
| `GET` | `/api/v1/business-analysis/{profile_id}/latest` | Retrieve latest analysis for business |
| `GET` | `/api/v1/approvals` | List regulatory approvals (filter by profile, status, priority) |
| `PATCH` | `/api/v1/approvals/{id}` | Update approval status/progress |
| `GET` | `/api/v1/tasks` | List compliance tasks |
| `POST` | `/api/v1/tasks` | Create compliance task |
| `PATCH` | `/api/v1/tasks/{id}/complete` | Mark compliance task as completed |
| `GET` | `/api/v1/documents` | List document vault items |
| `POST` | `/api/v1/documents` | Create document metadata |
| `GET` | `/api/v1/applications` | List statutory department applications |
| `POST` | `/api/v1/applications` | Submit new application |
| `GET` | `/api/v1/schemes` | List matched government schemes |
| `GET` | `/api/v1/alerts` | List compliance alerts & notifications |
| `PATCH` | `/api/v1/alerts/{id}/read` | Mark alert as read |
| `PATCH` | `/api/v1/alerts/read-all` | Mark all alerts as read |

---

## ⚠️ Prototype Disclaimer

> Recommendations are generated for prototype and planning purposes and should be verified with relevant statutory authorities.
