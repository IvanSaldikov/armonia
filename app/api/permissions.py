from typing import TYPE_CHECKING

from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

if TYPE_CHECKING:
    pass

IS_AUTHENTICATED = permissions.IsAuthenticated
IS_STAFF = permissions.IsAdminUser
ALLOW_ANY = permissions.AllowAny


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)


READ_ONLY = ReadOnly
