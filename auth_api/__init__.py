"""
Authentication API for Family Map Backend.

This Django app provides JWT-based authentication services for the Family Map backend.
It handles authentication concerns separately from domain-specific functionality,
following the separation of concerns principle.

Components:
- JWT authentication middleware for GraphQL requests
- Permission classes (IsAuthenticated, IsAdmin) for securing GraphQL fields
- GraphQL mutations for login, token refresh, and logout
- Token blacklisting for secure logout

This app is designed to be independent of specific domain models and can be
reused across different Django projects requiring JWT authentication for GraphQL.
"""
