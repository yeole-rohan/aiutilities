from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import User
from orgs.models import Membership, Organization


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "avatar_url", "date_joined")
        read_only_fields = ("id", "email", "date_joined")


class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "created_at")
        read_only_fields = ("id", "slug", "created_at")


@api_view(["GET"])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
def orgs_list(request):
    memberships = Membership.objects.filter(user=request.user).select_related("org")
    orgs = [m.org for m in memberships]
    return Response(OrgSerializer(orgs, many=True).data)
