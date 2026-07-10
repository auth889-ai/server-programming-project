# Workout Social API

SWE 4538 (Server Programming) — Group 14

A FastAPI social workout tracker: users register or sign in with Google,
post workouts, follow other athletes, and receive real-time feed updates
over SSE and WebSockets.

## Tech stack

- **FastAPI** + **SQLModel** (PostgreSQL via psycopg2)
- **JWT auth** (python-jose) with **argon2** password hashing
- **Google OAuth 2.0** login
- **Server-Sent Events** for the global hype stream and **WebSockets** for the personal feed
- **Redis** for rate limiting
- **Docker Compose** (PostgreSQL, Redis, nginx reverse proxy)

## Running

1. Create a `.env` file (never commit it):

   ```env
   SECRET_KEY=change_me
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   # optional overrides
   # DATABASE_URL=postgresql://swe_user:swe_pass@db:5432/swe_db
   # GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   # SQL_ECHO=true
   # REDIS_HOST=127.0.0.1
   # REDIS_PORT=6380
   ```

2. Start the infrastructure:

   ```bash
   docker compose up -d
   ```

3. Install dependencies and run the API:

   ```bash
   pip install -r requirements.txt
   uvicorn main:app --port 8001 --reload
   ```

   nginx (port 8000) proxies to the app on port 8001. Interactive docs
   are served at `http://localhost:8000/docs`, and `GET /health` is a
   simple liveness probe.

## API overview

| Area     | Endpoints                                                             |
|----------|-----------------------------------------------------------------------|
| Auth     | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `GET /api/auth/google/login`, `GET /api/auth/google/callback` |
| Users    | CRUD under `/api/users`, plus `/{id}/follow`, `/{id}/followers`, `/{id}/following` |
| Workouts | CRUD under `/api/workouts` (paginated list, owner-only edit/delete)   |
| Follows  | CRUD under `/api/follows`                                             |
| Feed     | `GET /api/feed/check-new` (polling), `GET /api/feed/stream/global-hype` (SSE), `WS /api/feed/ws/feed?token=...` |

Manual test pages for CORS, Google OAuth and the realtime feed live in `Test/`.
