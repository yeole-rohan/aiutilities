from django.conf import settings


def site_globals(request):
    domain = getattr(settings, "SITE_DOMAIN", "aiutilities.site")
    return {
        "SITE_DOMAIN": domain,
        "SITE_URL": f"https://{domain}",
    }
