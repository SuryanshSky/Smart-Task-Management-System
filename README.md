# TaskFlow — Smart Task Management System

A full-stack Python web application with Flask, PostgreSQL, WebSockets, Pandas/NumPy analytics, and a clean dark UI.

---

## Features

- **Authentication** — Register, login, logout with bcrypt password hashing
- **REST API** — Full CRUD for tasks (add, update, delete, get all) with filters & pagination
- **PostgreSQL** — Relational database with users and tasks tables
- **Analytics** — Pandas & NumPy-powered stats (total, completed, pending, completion %, trends)
- **WebSockets** — Real-time task notifications via Flask-SocketIO
- **Frontend** — Responsive dark UI with live updates, charts, and modals

---

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Backend      | Python 3.10+, Flask 3.0           |
| Database     | PostgreSQL 14+ via SQLAlchemy     |
| Auth         | Flask-Login, Flask-Bcrypt         |
| WebSockets   | Flask-SocketIO + Socket.IO        |
| Analytics    | Pandas 2.x, NumPy 1.26            |
| Frontend     | HTML5, CSS3, Vanilla JS           |
| Fonts        | Syne (display), DM Sans (body)    |

---

## Project Structure

```
task_manager/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # User & Task SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py          # Register, login, logout
│   │   ├── tasks.py         # REST API: CRUD for tasks
│   │   ├── analytics.py     # Pandas/NumPy analytics endpoint
│   │   ├── websocket.py     # SocketIO events
│   │   └── main.py          # Dashboard page
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── tasks/
│   │       └── dashboard.html
│   └── static/
│       └── css/
│           └── main.css
├── config.py                # Config classes
├── run.py                   # Entry point
├── schema.sql               # PostgreSQL schema
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip

### 2. Clone & Install

```bash
git clone <your-repo-url>
cd task_manager

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Start PostgreSQL and create the database
psql -U postgres
CREATE DATABASE taskmanager;
\q

# (Optional) Apply schema manually
psql -U postgres -d taskmanager -f schema.sql
```

### 4. Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values:
# SECRET_KEY=your-secret-key
# DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/taskmanager
```

### 5. Run the App

```bash
python run.py
```

Visit: http://localhost:5000

Flask-SQLAlchemy will auto-create tables on first run.

---

## REST API Reference

All task endpoints require login (`session` cookie from `/auth/login`).

### Authentication

| Method | Endpoint         | Description       |
|--------|-----------------|-------------------|
| POST   | /auth/register  | Register new user |
| POST   | /auth/login     | Login             |
| GET    | /auth/logout    | Logout            |
| GET    | /auth/me        | Current user info |

**Register body:**
```json
{ "username": "alice", "email": "alice@example.com", "password": "secret123" }
```

**Login body:**
```json
{ "email": "alice@example.com", "password": "secret123" }
```

---

### Tasks

| Method | Endpoint              | Description           |
|--------|-----------------------|-----------------------|
| GET    | /api/tasks/           | Get all tasks         |
| GET    | /api/tasks/?status=pending&priority=high | Filtered tasks |
| GET    | /api/tasks/{id}       | Get single task       |
| POST   | /api/tasks/           | Create task           |
| PUT    | /api/tasks/{id}       | Update task           |
| DELETE | /api/tasks/{id}       | Delete task           |

**Task object:**
```json
{
  "id": 1,
  "title": "Fix login bug",
  "description": "Users can't log in with uppercase email",
  "priority": "high",
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T11:00:00",
  "due_date": "2024-01-20T18:00:00",
  "user_id": 1
}
```

Priority values: `low`, `medium`, `high`
Status values: `pending`, `in_progress`, `completed`

---

### Analytics

| Method | Endpoint               | Description         |
|--------|------------------------|---------------------|
| GET    | /api/analytics/summary | Full analytics data |

**Response:**
```json
{
  "analytics": {
    "total_tasks": 20,
    "completed_tasks": 12,
    "pending_tasks": 5,
    "in_progress_tasks": 3,
    "completion_percentage": 60.0,
    "priority_breakdown": { "low": 4, "medium": 10, "high": 6 },
    "status_breakdown": { "pending": 5, "in_progress": 3, "completed": 12 },
    "avg_tasks_per_day": 2.5,
    "tasks_this_week": 7,
    "completion_trend": [
      { "day": "Mon", "count": 2 },
      ...
    ]
  }
}
```

---

## WebSocket Events

Connect with Socket.IO at `ws://localhost:5000`.

| Event          | Direction      | Description                      |
|----------------|----------------|----------------------------------|
| `connect`      | client → server | Join user's personal room       |
| `task_created` | server → client | New task created                |
| `task_updated` | server → client | Task updated                    |
| `task_deleted` | server → client | Task deleted                    |
| `ping_server`  | client → server | Health check                    |
| `pong_server`  | server → client | Health check response           |

---

## Running Tests

```bash
pip install pytest
pytest
```

---

## Environment Variables

| Variable       | Description                    | Default                       |
|----------------|-------------------------------|-------------------------------|
| `SECRET_KEY`   | Flask session secret          | *change this*                 |
| `DATABASE_URL` | PostgreSQL connection string  | localhost:5432/taskmanager    |
| `FLASK_ENV`    | development / production      | development                   |

---

## License

MIT
