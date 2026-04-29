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

Run migrations and start backend:

```bash
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000`.

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
```

### 4) Apply schema

```bash
python manage.py migrate
```

## Quick fallback for demo (SQLite)

If local PostgreSQL is not ready yet:

```bash
USE_SQLITE=true python manage.py migrate
USE_SQLITE=true python manage.py runserver
```
