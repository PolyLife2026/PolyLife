# PolyLife — Core

**One app, one complete lifestyle.**

Software Engineering 1 course project — 1404/1405.

---

## About PolyLife

PolyLife isn't just a fitness app — it's a smart, all-in-one ecosystem that turns the path to fitness, health, and well-being from a scattered, exhausting chore into a sustainable lifestyle. Our mission is to empower people to build the best version of themselves, by combining personalized workout programs, tailored diet plans, and the strength of a supportive social network.

The ecosystem is built from several specialized microservices, each designed to solve one specific need — and together they add up to one seamless experience:

| Service | Description |
|---|---|
| **PolyWorkout** | The core of your training: personalized, professional workout plans built around your goals |
| **PolyHomie** | Home or gym, either way — top-quality guided workouts |
| **PolyDiet** | Solid, budget-friendly meal plans and precise daily calorie tracking |
| **PolyBooking** | Your bridge to professionals — find and book sessions with expert trainers |
| **PolySocial** | A dedicated social network to connect with other athletes, share your journey, and stay motivated |
| **PolyGroupie** | Exciting group workouts and classes |
| **PolyChallenge** | Gamified fitness challenges and in-app competitions to keep you motivated |
| **PolyProgress** | Smart tracking of your physical progress and personal records over time |
| **PolyAnalysis** | Intelligent analysis of injury risk and nutritional risk, keeping your health journey as safe as possible |
| **PolyShop** | Your dedicated store for supplements and equipment, with a unified cart and secure checkout |

> With PolyLife, excuses run out and change begins. Build your healthy self.

This repository is the **Core** of that ecosystem: the shared infrastructure — authentication, the landing page, and the auth gateway — behind every team microservice. Each student team builds its own service, with its own database and its own gateway, behind this core.

---

## Architecture

```
 browser ───────────────▶ Core (Django)               http://localhost:8000
                           • React landing page (SPA)
                           • /api/register | login | user
                           • /api/verify  (forward-auth for teams)
                                  ▲
 browser ─▶ team gateway (nginx) ─┘  http://localhost:910N
              │
              ▼
           team backend ──▶ team's own database (with a unique password)
```

Auth: `username + password → JWT`. The core verifies the token; teams never decode JWTs — their gateway calls `/api/verify` and forwards the `X-User-*` headers to the backend.

## Suggested flow

1. **Register** — `POST /api/register` with `{"username": "ali", "password": "Sup3rSecretPass"}`
2. **Login** — `POST /api/login` with the same credentials. The response returns `token`/`refresh` and sets an `HttpOnly` access cookie so browser sessions also work through team gateways on ports 9101…9108.
3. **Get user** — `GET /api/user` with `Authorization: Bearer <token>`
4. **Refresh** — `POST /api/refresh` with `{"refresh": "<refresh>"}` → a fresh token
5. **Verify** — `GET /api/verify` with the Bearer token → check the `X-User-*` response headers (this is what a team gateway calls)
6. **Logout** — `POST /api/logout` with the Bearer token. Afterwards, the same token/refresh stop working.

> **Isolation:** each team has its own database with its own user/password.

## Layout

| Path | Description |
|---|---|
| `polylife/` | Django project (settings, urls, per-team DB router) |
| `core/` | core app: User model, JWT, auth API, middleware, verify |
| `frontend/` | React/Vite landing page (built inside Docker) |
| `teams/` | the 8 team templates — student guide: `teams/GETTING_STARTED.md` |
| `scripts/` | helper scripts to start/stop the core and teams (`windows/`, `bash/`) |

## Run (with Docker — recommended)

```powershell
scripts\windows\start-core.ps1        # core      → http://localhost:8000
scripts\windows\start-team.ps1 1      # one team  → http://localhost:9101
scripts\windows\start-all-teams.ps1   # all 8 teams (9101..9108)
```

Stop:

```powershell
scripts\windows\stop-core.ps1
scripts\windows\stop-team.ps1 1
scripts\windows\stop-all.ps1          # everything
```

Bash equivalents live in `scripts/bash/*.sh`.

**Seeded demo users:** `user1/user1pass`, `user2/user2pass`, `user3/user3pass`

## Run the core without Docker

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

> The React page only renders when built in Docker; locally you get a fallback page plus the fully working API.

## Tests

```powershell
.\.venv\Scripts\python.exe manage.py test core
```

To exercise the API by hand (Postman / curl), see `docs/API_TESTING.md`.

## Configuration

For local settings, copy `.env.example` to `.env`. No secret is ever committed.
