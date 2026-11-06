# SocioSolve — AI-Powered Societal Problem-Solving Platform

> **Connect citizens, students, universities, NGOs, and companies to identify real-world societal problems and build practical, collaborative solutions — powered by AI.**

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Quick Start (Windows)](#quick-start-windows)
- [Environment Variables](#environment-variables)
- [Demo Credentials](#demo-credentials)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [AI Features](#ai-features)
- [Security Notes](#security-notes)
- [Documentation](#documentation)

---

## Project Overview

SocioSolve is a collaborative Django web application that:

1. Lets authenticated users **report societal challenges** (environment, healthcare, education, water conservation, etc.)
2. Uses **Mistral AI** to analyze challenges, generate solution roadmaps, find similar challenges, and recommend collaborators
3. Provides **team workspaces** with Kanban tasks, milestones, and progress tracking
4. Supports **university/company partnerships** and sponsored challenges
5. Displays a **live impact dashboard** backed entirely by real database records — no hardcoded statistics

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Django 5.1 |
| Database | SQLite (dev) / PostgreSQL (production) |
| Frontend | Django Templates, Bootstrap 5.3, Chart.js, Bootstrap Icons |
| AI | Mistral AI API (chat completions + embeddings) |
| Auth | Django's built-in auth + custom User model |
| Environment | python-dotenv |
| Testing | Django TestCase (27 tests) |

---

## Features

### Authentication & Roles
- Registration, login, logout, password change
- Six roles: Citizen, Student, University, Company, NGO, Administrator
- Role-based access control enforced server-side
- User profiles with skills, interests, bio, avatar

### Challenge Management
- Create, edit, delete challenges (owner/admin only)
- Categories: Environment, Education, Healthcare, Transportation, Water Conservation, Waste Management, Public Safety, Other
- Search, filter, sort, pagination
- Image upload (validated type + size)
- Bookmarking and reporting/moderation

### AI Features (requires Mistral API key)
- **AI Challenge Analyzer** — root causes, stakeholders, priority, missing info
- **AI Solution Generator** — 5 detailed roadmaps with risks, resources, impact metrics
- **Similar Challenge Finder** — semantic search (embeddings) with keyword fallback
- **Smart Team Matcher** — recommends collaborators with reasoning
- Graceful degradation when API key is missing
- Per-user rate limiting, input validation, ethical disclaimer
- Analysis cached on challenge model to avoid repeat API calls

### Collaboration
- Solution proposals with upvote/downvote (1 vote per user)
- Threaded comments and discussion
- Team creation, join requests, membership approval
- Kanban task board (To-Do / In Progress / Completed / Blocked)
- Milestones with completion tracking

### Partnerships & Sponsorships
- Organization profiles (university/company/NGO)
- Partnership requests between organizations and challenge teams
- Sponsored challenges

### Impact Dashboard
- Live database-backed statistics
- Chart.js visualizations (category breakdown, monthly trends, team activity)
- Verified vs self-reported impact clearly distinguished
- Individual impact reports per project team

---

## Quick Start (Windows)

### Prerequisites
- Python 3.11 or later — https://www.python.org/downloads/
- Git (optional)

### 1. Clone or Extract the Project

```powershell
cd C:\Users\YourName\Desktop
# If using Git:
git clone <repository-url> SocioSolver
cd SocioSolver
# Or just cd into the extracted folder
cd SocioSolver
```

### 2. Create and Activate Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If you get an execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```powershell
copy .env.example .env
```

Open `.env` in a text editor and fill in your values:

```
SECRET_KEY=your-secret-key-here
MISTRAL_API_KEY=your-mistral-api-key-here   # Optional — AI features degrade gracefully without it
```

To generate a Django secret key:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Apply Migrations

```powershell
python manage.py migrate
```

### 6. Create a Superuser (Optional — demo data includes an admin)

```powershell
python manage.py createsuperuser
```

### 7. Load Demo Data

```powershell
python manage.py load_demo_data
```

This creates 8 categories, 6 demo users (all roles), 3 challenges with AI analysis cache, proposals, votes, a team with tasks and milestones, partnerships, and 2 impact reports.

### 8. Start the Development Server

```powershell
python manage.py runserver
```

Open your browser to: **http://127.0.0.1:8000/**

Admin panel: **http://127.0.0.1:8000/admin/**

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | `True` for dev, `False` for production (default: `True`) |
| `ALLOWED_HOSTS` | No | Comma-separated hosts for production |
| `MISTRAL_API_KEY` | No | Mistral API key — AI features disabled gracefully without it |
| `MISTRAL_MODEL` | No | Chat model (default: `mistral-small-latest`) |
| `MISTRAL_EMBEDDING_MODEL` | No | Embedding model (default: `mistral-embed`) |
| `DATABASE_URL` | No | PostgreSQL URL for production (falls back to SQLite) |
| `MAX_AI_REQUESTS_PER_HOUR` | No | Per-user AI rate limit (default: 15) |

See `.env.example` for a full template.

---

## Demo Credentials

All demo users use the password: **`SocioSolve2026!`**

| Username | Role | Notes |
|----------|------|-------|
| `admin_socio` | Administrator | Full access + Django admin |
| `maya_student` | Student | Active challenger |
| `raj_citizen` | Citizen | Community reporter |
| `prof_kumar` | University | University representative |
| `techcorp_rep` | Company | Corporate partner |
| `green_ngo` | NGO | Environmental NGO |

> **Note:** Demo accounts are clearly labeled `[DEMO]` in the application and are for demonstration purposes only.

---

## Running Tests

```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test accounts
python manage.py test challenges
python manage.py test solutions
python manage.py test collaboration
python manage.py test impact
python manage.py test ai_services

# Run with verbosity
python manage.py test --verbosity=2
```

**Expected result:** 27 tests, 0 failures, 0 errors

AI tests use mocked API calls — no internet connection or API credits required.

---

## Project Structure

```
SocioSolver/
├── sociosolve_core/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                 # Custom user model, auth, profiles
├── challenges/               # Challenge CRUD, search, moderation
├── solutions/                # Proposals, voting, comments
├── collaboration/            # Teams, tasks, milestones
├── partnerships/             # Org profiles, partnerships, sponsorships
├── impact/                   # Impact dashboard, reports
├── ai_services/              # AI integration module
├── templates/                # All HTML templates
│   ├── base.html
│   ├── navbar.html
│   ├── footer.html
│   ├── landing.html
│   ├── accounts/
│   ├── challenges/
│   ├── solutions/
│   ├── collaboration/
│   ├── partnerships/
│   ├── impact/
│   ├── ai_services/
│   └── errors/
├── static/
│   ├── css/style.css
│   └── js/main.js
├── media/                    # User-uploaded files (gitignored)
├── docs/                     # Documentation
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## AI Features

AI features require a Mistral API key in your `.env` file.

When no API key is configured:
- The UI shows a clear "AI features require configuration" message
- All non-AI features continue to work normally
- No fake results are ever shown

When an API key is present:
- Challenge analysis results are cached on the challenge model to avoid repeat calls
- Embeddings are stored for semantic search
- Rate limiting prevents abuse (15 requests/user/hour by default)
- All AI output includes an ethical disclaimer

See `docs/AI_INTEGRATION.md` for full details.

---

## Security Notes

- Never commit your `.env` file (it is in `.gitignore`)
- The `SECRET_KEY` in `.env.example` is a placeholder — generate a new one
- CSRF protection is enabled on all forms
- File uploads validate type (images only) and size (max 5 MB)
- Server-side permission checks on all sensitive views
- One vote per user per proposal enforced at the database level

For production deployment settings, see `docs/ARCHITECTURE.md`.

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/ER_DIAGRAM.md` | Entity-relationship diagram of all database models |
| `docs/ARCHITECTURE.md` | Project architecture and deployment guide |
| `docs/AI_INTEGRATION.md` | AI feature documentation and configuration |
| `docs/TEST_INSTRUCTIONS.md` | Testing guide and test descriptions |
| `docs/INTERVIEW_PREP.md` | Technical interview preparation guide |

---

## License

This project was built as an educational and portfolio demonstration. All AI-generated content is labeled with appropriate disclaimers. Do not use demo credentials or sample data in production.
#   S o c i o S o l v e r  
 