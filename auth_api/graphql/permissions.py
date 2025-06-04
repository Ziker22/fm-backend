"""
Permission classes for GraphQL API authentication and authorization.

This module provides reusable permission classes that can be used with
Strawberry GraphQL to protect fields and mutations based on authentication
status and user roles.
"""
import typing

import strawberry
from django.contrib.auth.models import AnonymousUser
from strawberry.permission import BasePermission
from strawberry.types import Info

from users.models import UserRole


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        if info.context['request'] is None:
            return False
        is_authenticated = info.context['request'].user.pk is not None
        return is_authenticated


class IsAdmin(BasePermission):
    message = "User is not authorized to access this resource"

    # This method can also be async!
    def has_permission(
        self, source: typing.Any, info: strawberry.Info, **kwargs
    ) -> bool:
        if info.context['request'] is None:
            return False
        role  = info.context.request.user.role
        return role == UserRole.ADMIN
