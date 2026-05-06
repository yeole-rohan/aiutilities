from .base import *  # noqa: F401, F403

DEBUG = True
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

ACCOUNT_EMAIL_VERIFICATION = "optional"
CELERY_TASK_ALWAYS_EAGER = True  # run tasks synchronously in dev
