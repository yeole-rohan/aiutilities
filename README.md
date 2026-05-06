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
cp .env.example .env   # fill in SECRET_KEY and DATABASE_URL at minimum
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000

## Docker

```bash
cp .env.example .env
docker compose up --build
```

Services started: `web`, `postgres`, `redis`, `celery`, `celery-beat`.

## Version support

- Python 3.11 / 3.12 / 3.13
- Django 4.2 LTS

## Documentation

Full setup guide including Google OAuth, Stripe, Lemon Squeezy, and deployment:
https://djangoproject.in/saas-starter/docs/

## License

Paid license — see your purchase confirmation for terms.
One license per project (Starter) or unlimited projects (Lifetime).
