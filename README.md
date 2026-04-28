# User Service

Microservice responsible for user registration, authentication, and profile management. Part of the **Live Streaming Platform** built for SEZG583 — Scalable Services assignment.

---

## Overview

| Property | Value |
|----------|-------|
| Language | Python 3.11 |
| Framework | FastAPI |
| Database | PostgreSQL |
| Auth | JWT (access + refresh tokens) |
| Messaging | RabbitMQ (publishes `user.registered` events) |
| Port | 8000 |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |

### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/users/me` | Get my profile | ✅ |
| PUT | `/api/v1/users/me` | Update my profile | ✅ |
| DELETE | `/api/v1/users/me` | Deactivate account | ✅ |
| GET | `/api/v1/users/validate` | Validate JWT (used by Stream Service) | ✅ |
| GET | `/api/v1/users/{username}` | Get public profile | ❌ |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

---

## Project Structure

```
user-service/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/v1/
│   │   ├── auth.py              # Register, login, refresh endpoints
│   │   └── users.py             # Profile endpoints
│   ├── core/
│   │   ├── config.py            # Settings via pydantic-settings
│   │   └── security.py          # JWT create/decode, bcrypt hashing
│   ├── db/
│   │   └── database.py          # SQLAlchemy engine + session
│   ├── models/
│   │   └── user.py              # SQLAlchemy User model
│   ├── schemas/
│   │   └── user.py              # Pydantic request/response schemas
│   └── services/
│       ├── user_service.py      # Business logic
│       └── event_publisher.py   # RabbitMQ event publisher
├── alembic/                     # Database migrations
│   └── versions/
│       └── 0001_initial.py      # Initial users table migration
├── tests/
│   ├── conftest.py              # Test fixtures (SQLite in-memory)
│   └── test_auth.py             # Auth endpoint tests
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── .env.example
```

---

## Running Locally

### With Docker Compose (recommended)

From the root `livestream/` folder:

```bash
docker compose up --build
```

User Service will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Without Docker (development)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Running Tests

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests/ -v
```

Tests use SQLite in-memory — no PostgreSQL required.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/userdb` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `RABBITMQ_URL` | RabbitMQ connection string | `amqp://guest:guest@localhost:5672/` |

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Inter-Service Communication

### Sync (REST)
Stream Service calls `GET /api/v1/users/validate` with a Bearer token to verify JWT without sharing the secret key.

### Async (RabbitMQ)
Publishes to `user_events` fanout exchange on these events:
- `user.registered` — when a new user registers

---

## Docker

```bash
# Build
docker build -t user-service:latest .

# Run
docker run -p 8000:8000 --env-file .env user-service:latest
```

---

## Related Repositories

- [livestream-stream-service](https://github.com/YOUR_USERNAME/livestream-stream-service) — Stream lifecycle + Ant Media Server integration
