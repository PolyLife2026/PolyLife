PolyLife — Core

One application, one complete lifestyle.

Software Engineering 1 Course Project — Semester 1404/1405
About PolyLife

PolyLife is not just a fitness application; it is a smart, integrated ecosystem that transforms the journey toward fitness, health, and vitality from a scattered and exhausting challenge into a sustainable lifestyle. Our mission is to empower people to build the best version of themselves by combining workout programs, personalized nutrition plans, and the strength of a supportive social network.

This ecosystem consists of several specialized services (microservices), each carefully designed to address a specific user need while collectively delivering a seamless experience:
Service 	Description
PolyWorkout 	The central training core; personalized workout plans based on the user’s goals
PolyHomie 	High-quality training experiences at home or in the gym
PolyDiet 	Structured diet plans and accurate daily calorie tracking
PolyBooking 	Session booking with coaches and specialists
PolySocial 	A dedicated social network for connection and motivation among athletes
PolyGroupie 	Group workouts and classes
PolyChallenge 	In-app challenges and competitions with a gamification approach
PolyProgress 	Tracking body progress and athletic records
PolyAnalysis 	Intelligent analysis of injury risks and nutritional hazards
PolyShop 	A sports supplements and equipment store with an integrated shopping cart

    With PolyLife, excuses come to an end and transformation begins. Build your own healthy lifestyle!

This repository contains the Core of the ecosystem: the shared infrastructure for all services — including authentication, the landing page, and the authentication gateway for student-team microservices. Each team builds its own service, with its own database and dedicated gateway, behind this common core.
Architecture

                                                                    text
 browser ───────────────▶ Core (Django)               http://localhost:8000
                           • React landing page (SPA)
                           • /api/register | login | user
                           • /api/verify  (forward-auth for teams)
                                  ▲
 browser ─▶ team gateway (nginx) ─┘  http://localhost:910N
              │
              ▼
           team backend ──▶ team's own database (with a unique password)

Authentication flow: username + password → JWT.

The core validates the token; teams never decode the JWT themselves — each team gateway calls /api/verify and forwards the X-User-* headers to its own backend.
Suggested Usage Flow

    Register — POST /api/register with body {"username": "ali", "password": "Sup3rSecretPass"}
    Login — POST /api/login with the same credentials. The response includes token / refresh, and an HttpOnly cookie is also set so browser sessions can work through team gateways as well (ports 9101 to 9108).
    Get User — GET /api/user with header Authorization: Bearer <token>
    Refresh Token — POST /api/refresh with {"refresh": "<refresh>"} → returns a new token
    Verify — GET /api/verify with Bearer token → inspect the response headers X-User-* (this is what each team gateway calls)
    Logout — POST /api/logout with Bearer token. After that, the same token / refresh pair will no longer work.

    Isolation: Each team has its own independent database with a dedicated username/password.

Project Structure
Path 	Description
polylife/ 	Django project (settings, URLs, per-team database router)
core/ 	Core app: User model, JWT, authentication APIs, middleware, verify
frontend/ 	React/Vite landing page (built inside Docker)
teams/ 	8 team templates — student guide: teams/GETTING_STARTED.md
scripts/ 	Helper scripts for starting/stopping the core and teams (windows/, bash/)
Running with Docker — Recommended Method

                                                                    powershell
scripts\windows\start-core.ps1        # core      → http://localhost:8000
scripts\windows\start-team.ps1 1      # one team  → http://localhost:9101
scripts\windows\start-all-teams.ps1   # all 8 teams (9101..9108)

Stop:

                                                                    powershell
scripts\windows\stop-core.ps1
scripts\windows\stop-team.ps1 1
scripts\windows\stop-all.ps1          # everything

Bash equivalents are available in scripts/bash/*.sh.

Seeded demo users: user1/user1pass, user2/user2pass, user3/user3pass
Running the Core Without Docker

                                                                    powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver

    The React page is rendered only when it has been built inside Docker; in local execution, you will get a fallback page alongside a fully functional API.

Tests

                                                                    powershell
.\.venv\Scripts\python.exe manage.py test core

For manual API testing with Postman / curl, see docs/API_TESTING.md.
Configuration

For local settings, copy .env.example to .env. No secrets are committed.
