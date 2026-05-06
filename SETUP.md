# Setup Checklist

Read this before writing a single line of your app code.
Work through these steps in order — most issues come from skipping one.

---

## 1. Clone and install

```bash
git clone git@github.com:YOUR_ORG/saas-starter.git myapp
cd myapp
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

## 2. Configure environment

```bash
cp .env.example .env
```

Set `SECRET_KEY` — generate one:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then choose **one** of the two paths below.

---

### Path A — Local (no Docker)

**Option A1: SQLite** (fastest start, no installs)

`.env` default is already set to SQLite — nothing else to change:
```
DATABASE_URL=sqlite:///db.sqlite3
```
Skip to step 4.

**Option A2: Local PostgreSQL**

Install postgres if you haven't already:
```bash
# Ubuntu / Debian / WSL
sudo apt update && sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql

# macOS (Homebrew)
brew install postgresql@16
brew services start postgresql@16
```

Create the user and database:
```bash
# Ubuntu / Debian / WSL
sudo -u postgres psql <<SQL
CREATE USER saas WITH PASSWORD 'saas';
CREATE DATABASE saas OWNER saas;
GRANT ALL PRIVILEGES ON DATABASE saas TO saas;
SQL

# macOS
psql postgres -c "CREATE USER saas WITH PASSWORD 'saas';"
psql postgres -c "CREATE DATABASE saas OWNER saas;"
```

Update `.env`:
```
DATABASE_URL=postgres://saas:saas@localhost:5432/saas
```

Skip to step 4.

---

### Path B — Docker Compose

`docker-compose.yml` sets `DATABASE_URL` and `REDIS_URL` automatically for all services — you do **not** need to set them in `.env`. The `db` hostname only resolves inside Docker's internal network; using it outside Docker causes:

```
django.db.utils.OperationalError: could not translate host name "db"
```

Keep `.env` as-is (SQLite default is fine — it is ignored when Docker runs). Skip to step 3 (Docker).

## 3. Start with Docker (Path B only)

```bash
docker compose up --build
```

This starts `web`, `db` (postgres 16), `redis`, `celery`, and `celery-beat`.
Migrations run automatically on first boot. Open http://localhost:8000.

```bash
# Create a superuser
docker compose exec web python manage.py createsuperuser
```

Skip to step 5 (tests).

---

## 4. Run migrations (Path A only)

The project directory is `saas_starter/`. To rename to `myapp/`:

```bash
mv saas_starter myapp
# Then find+replace all occurrences of "saas_starter" in:
# manage.py, myapp/wsgi.py, myapp/celery.py, myapp/__init__.py, setup.cfg
grep -r "saas_starter" . --include="*.py" --include="*.cfg" -l
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://localhost:8000/ (landing page) and http://localhost:8000/admin/.

## 5. Run the test suite

Tests use an in-memory SQLite database — no postgres or Docker needed:

```bash
pytest
```

All 42 tests should pass. CI runs the same command. If you see database
connection errors, make sure you haven't set `DJANGO_SETTINGS_MODULE` to
something other than `saas_starter.settings.test` in your shell.

## 6. Configure Google OAuth

1. Go to https://console.cloud.google.com/ → APIs & Services → Credentials
2. Create an OAuth 2.0 Client ID (Web application)
3. Add `http://localhost:8000/accounts/google/login/callback/` to Authorised redirect URIs
4. Add your production domain callback too: `https://yourdomain.com/accounts/google/login/callback/`
5. Copy Client ID and Client Secret to `.env`:
   ```
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```

## 7. Configure Stripe billing

1. Create a Stripe account and products at https://dashboard.stripe.com/
2. Create two prices (Pro monthly, Team monthly)
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRO_PRICE_ID=price_...
   STRIPE_TEAM_PRICE_ID=price_...
   ```
4. Run: `python manage.py djstripe_sync_models`
5. Register webhook at Stripe Dashboard → `https://yourdomain.com/billing/stripe/webhook/`
   Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`

## 8. Configure Lemon Squeezy (India / global alternative)

1. Create a store at https://app.lemonsqueezy.com/
2. Create products with Pro and Team variants
3. Add to `.env`:
   ```
   LEMON_SQUEEZY_SIGNING_SECRET=...
   LS_PRO_VARIANT_ID=...
   LS_TEAM_VARIANT_ID=...
   ```
4. Register webhook: `https://yourdomain.com/billing/lemonsqueezy/webhook/`
   Events: `subscription_created`, `subscription_updated`, `subscription_cancelled`

Pass `custom_data: { org_id: "123" }` in the checkout URL so the webhook knows which org to activate.

## 9. Configure email

For development, `console` backend prints emails to stdout — no config needed.

For production (example using Postmark):
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.postmarkapp.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-api-token
EMAIL_HOST_PASSWORD=your-api-token
DEFAULT_FROM_EMAIL=hello@yourdomain.com
```

## 10. Customize the DaisyUI theme

Open `templates/base.html` and change `data-theme` on the `<html>` tag.
Available themes: https://daisyui.com/docs/themes/
No build step needed.

## 11. Customize plans

Edit `billing/models.py` → `Plan` choices.
Update `billing/backends/stripe_backend.py` and `lemonsqueezy.py` to map your variant IDs to plan slugs.
Update the upgrade page template (`templates/billing/upgrade.html`) with correct prices.

## 12. Deploy

See `deploy/` for nginx config and systemd service files.
See `docker-compose.yml` for Docker-based deployment.
Full docs: https://djangoproject.in/saas-starter/docs/deployment/

---

## Settings files

| File | Used for |
|---|---|
| `saas_starter/settings/base.py` | Shared settings for all environments |
| `saas_starter/settings/development.py` | Local development (debug toolbar, eager Celery) |
| `saas_starter/settings/test.py` | Test suite (SQLite in-memory, no external services) |
| `saas_starter/settings/production.py` | Production (set via `DJANGO_SETTINGS_MODULE` on server) |

`pytest` uses `test.py` automatically (configured in `setup.cfg`).
Your dev server uses `development.py` — set `DJANGO_SETTINGS_MODULE=saas_starter.settings.development` in your shell or `.env`.

---

## What to search for

All points where you need to add your own logic are marked with:

```python
# CUSTOMIZE: ...
```

Run `grep -r "# CUSTOMIZE" . --include="*.py" --include="*.html"` to find them all.
