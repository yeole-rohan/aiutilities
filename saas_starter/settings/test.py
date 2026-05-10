from .base import *  # noqa: F401, F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Skip email sending during tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Skip email verification so auth tests don't require confirmation flow
ACCOUNT_EMAIL_VERIFICATION = "none"

# Suppress whitenoise manifest lookup errors on missing staticfiles
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
