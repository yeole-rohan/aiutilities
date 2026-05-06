from django.contrib import admin

from .models import Invite, Membership, Organization


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    raw_id_fields = ("user",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "created_at")
    search_fields = ("name", "slug")
    raw_id_fields = ("owner",)
    inlines = [MembershipInline]


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ("email", "org", "role", "is_accepted", "created_at")
    list_filter = ("role",)
    search_fields = ("email",)
    readonly_fields = ("token",)
