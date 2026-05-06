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

Open `.env` and fill in:

- `SECRET_KEY` — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DATABASE_URL` — your PostgreSQL connection string
- `REDIS_URL` — your Redis URL

Leave billing and OAuth keys blank for now — you can add them when you're ready.

## 3. Rename the project (optional but recommended)

The project directory is `saas_starter/`. To rename to `myapp/`:

```bash
mv saas_starter myapp
# Then find+replace all occurrences of "saas_starter" in:
# manage.py, myapp/wsgi.py, myapp/celery.py, myapp/__init__.py
grep -r "saas_starter" . --include="*.py" -l
```

## 4. Run migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://localhost:8000/ (landing page) and http://localhost:8000/admin/.

## 5. Configure Google OAuth

1. Go to https://console.cloud.google.com/ → APIs & Services → Credentials
2. Create an OAuth 2.0 Client ID (Web application)
3. Add `http://localhost:8000/accounts/google/login/callback/` to Authorised redirect URIs
4. Add your production domain callback too: `https://yourdomain.com/accounts/google/login/callback/`
5. Copy Client ID and Client Secret to `.env`:
   ```
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```

## 6. Configure Stripe billing

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

## 7. Configure Lemon Squeezy (India / global alternative)

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

## 8. Configure email

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

## 9. Customize the DaisyUI theme

Open `templates/base.html` and change `data-theme` on the `<html>` tag.
Available themes: https://daisyui.com/docs/themes/
No build step needed.

## 10. Customize plans

Edit `billing/models.py` → `Plan` choices.
Update `billing/backends/stripe_backend.py` and `lemonsqueezy.py` to map your variant IDs to plan slugs.
Update the upgrade page template (`templates/billing/upgrade.html`) with correct prices.

## 11. Deploy

See `deploy/` for nginx config and systemd service files.
See `docker-compose.yml` for Docker-based deployment.
Full docs: https://djangoproject.in/saas-starter/docs/deployment/

---

## What to search for

All points where you need to add your own logic are marked with:

```python
# CUSTOMIZE: ...
```

Run `grep -r "# CUSTOMIZE" . --include="*.py" --include="*.html"` to find them all.
