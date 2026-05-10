from django.urls import path

from . import views

app_name = "tools"

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:category_slug>/", views.category, name="category"),
    path("<slug:category_slug>/<slug:tool_slug>/", views.tool, name="tool"),
]
