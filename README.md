# Django SaaS Starter

A production-ready Django boilerplate for indie hackers and bootstrapped founders. Auth, teams, billing, and infra — all wired up. You own the code.

## What's included

| Module | Stack |
|---|---|
| Auth | django-allauth · email + password · Google OAuth · email verification |
| Teams | Organizations · roles (owner / admin / member) · email invites |
| Billing | Stripe via dj-stripe · Lemon Squeezy (India/global) · subscription gating |
| API | Django REST Framework · SimpleJWT · per-user API keys |
| Background tasks | Celery · Redis · async email tasks |
| Admin | DaisyUI-themed admin panel |
| Frontend | Tailwind CSS + DaisyUI via CDN · HTMX · no Node build step |
| Infrastructure | Docker Compose · Gunicorn · WhiteNoise · nginx · systemd · GitHub Actions CI |

## Quick start

```bash
git clone <this-repo> myapp
cd myapp
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env   # set SECRET_KEY; DATABASE_URL defaults to SQLite for quick start
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000

## Run tests

Tests use SQLite in-memory — no postgres or Docker required:

```bash
pytest
```

## Docker

```bash
cp .env.example .env   # uses postgres + redis via Docker by default
docker compose up --build
```

Services started: `web`, `postgres`, `redis`, `celery`, `celery-beat`.

## Settings

| Module | Purpose |
|---|---|
| `settings/base.py` | Shared configuration |
| `settings/development.py` | Local dev — debug toolbar, eager Celery |
| `settings/test.py` | Test suite — SQLite in-memory, no external services |
| `settings/production.py` | Production — configure via environment variables |

## Version support

| | Supported |
|---|---|
| Python | 3.11 · 3.12 · 3.13 |
| Django | 4.2 LTS |

## Documentation

Full setup guide — Google OAuth, Stripe, Lemon Squeezy, deployment:
https://djangoproject.in/saas-starter/docs/

## License

Paid licence — see your purchase confirmation for terms.
Starter: one project. Lifetime: unlimited projects.
