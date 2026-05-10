from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .registry import CATEGORIES, get_all_tools


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ["tools:index", "accounts:landing"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [c["slug"] for c in CATEGORIES]

    def location(self, slug):
        return reverse("tools:category", args=[slug])


class ToolSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return get_all_tools()

    def location(self, item):
        cat, tool = item
        return reverse("tools:tool", args=[cat["slug"], tool["slug"]])
