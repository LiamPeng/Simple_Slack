# CS6083 Workspace Messaging Project

React frontend + Django REST API backend + PostgreSQL database.

## Project structure

```text
Simple_Slack/
├── backend/                 # Django project
│   ├── settings.py
│   ├── urls.py
│   └── apps/                # Domain apps (accounts/workspaces/channels/messages/invitations)
├── frontend/                # Vite + React frontend
├── diagrams/                # ER diagrams from Project 1
├── sql/                     # Project 1 SQL artifacts
├── report/
└── output/
```

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 14+ (local)

## Backend setup (Django)

From project root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if present
```

If `requirements.txt` is not present, install the core backend packages manually:

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary
```

Create and load environment variables:

```bash
cp .env.example .env  # if available
set -a
source .env
set +a
```

Required backend env values (minimum):

```env
DJANGO_SECRET_KEY=replace-with-a-secure-secret-key
```

Run migrations and start backend:

```bash
python manage.py migrate
```

**WebSockets (live messages)** require an ASGI server. From the project root, **activate the project venv** and run Daphne **via that Python** (not Homebrew’s global `daphne`, which will miss `psycopg2` and other venv packages):

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m daphne -b 127.0.0.1 -p 8000 backend.asgi:application
```

For quick HTTP-only checks you can still use `python manage.py runserver`, but channel pages will not receive live updates without Daphne (or another ASGI host).

Backend runs at `http://127.0.0.1:8000`.

**Optional: Redis channel layer** (needed when you run multiple backend processes so WebSocket broadcasts reach every worker). Set `REDIS_URL` (for example `redis://127.0.0.1:6379/0`) in the environment; otherwise the app uses an in-memory layer suitable for a single process.

**Existing databases:** the domain app for Slack-style channels is registered in Django as `slack_channels` (not `channels`) so it does not clash with the Django Channels package. Run `python manage.py migrate` after pulling: migration `slack_channels.0002_use_legacy_channel_table_names` keeps physical PostgreSQL/SQLite tables named `channels_channel` and `channels_channelmembership` (either by renaming from `slack_channels_*` or leaving legacy names unchanged). If `GET /api/workspaces/<id>/` returns 500, a missing or mismatched channel table is a common cause; applying migrations fixes it for most setups.

### Troubleshooting

**`InconsistentMigrationHistory: chat_messages.0001_initial is applied before its dependency slack_channels.0001_initial`**

Your database was migrated when the channel app was still labeled `channels`. Align history, then migrate:

1. If `django_migrations` still has rows with `app = 'channels'`, rename them to `slack_channels` (PostgreSQL example):

   ```sql
   UPDATE django_migrations SET app = 'slack_channels' WHERE app = 'channels';
   ```

2. If there is **no** `channels` row but `slack_channels.0001_initial` is missing while `chat_messages.0001_initial` is applied, mark the channel initial migration as already applied (tables must already exist):

   ```bash
   python manage.py migrate slack_channels 0001_initial --fake
   ```

3. Then run:

   ```bash
   python manage.py migrate
   ```

**`ImproperlyConfigured: Error loading psycopg2` when running `daphne`**

You are using a **global** Daphne (e.g. `/opt/homebrew/bin/daphne`) instead of the venv. Use `python -m daphne` after `source .venv/bin/activate` and `pip install -r requirements.txt` (see WebSockets block above).

## Frontend setup (React + Vite)

From `frontend/`:

```bash
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Recommended frontend env values:

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_USE_MOCK=false
```

Optional: set `VITE_WS_URL` if the WebSocket origin differs from the API URL (otherwise the client derives `ws` / `wss` from `VITE_API_URL`).

## Local PostgreSQL setup

### 1) Start PostgreSQL (Homebrew on macOS)

```bash
brew services start postgresql@16
```

### 2) Create database user and database

Open `psql` with a superuser and run:

```sql
CREATE ROLE your_pg_user WITH LOGIN PASSWORD 'your_pg_password';
CREATE DATABASE simple_slack OWNER your_pg_user;
```

### 3) Configure `.env`

```env
DB_NAME=simple_slack
DB_USER=your_pg_user
DB_PASSWORD=your_pg_password
DB_HOST=localhost
DB_PORT=5432
FRONTEND_ORIGIN=http://localhost:5173
DJANGO_SECRET_KEY=replace-with-a-secure-secret-key
```

### 4) Apply schema

```bash
python manage.py migrate
```

## Quick fallback for demo (SQLite)

If local PostgreSQL is not ready yet:

```bash
python manage.py migrate
python manage.py runserver
```
