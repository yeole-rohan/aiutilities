from django.http import Http404
from django.urls import path

from . import views
from .ai_views import AI_HANDLERS


def ai_generate(request, category_slug, tool_slug):
    handler = AI_HANDLERS.get(tool_slug)
    if not handler:
        raise Http404
    return handler(request)


app_name = "tools"

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:category_slug>/", views.category, name="category"),
    path("<slug:category_slug>/<slug:tool_slug>/generate/", ai_generate, name="ai_generate"),
    path("<slug:category_slug>/<slug:tool_slug>/", views.tool, name="tool"),
]
