# User Registration & Roles via GraphQL

This document describes how to register a new user in the Family-Map backend using the GraphQL API powered by Strawberry-Django **and** how role-based access control (RBAC) works for user-related queries.

---

## 1. GraphQL Endpoint

```
POST /graphql/
Content-Type: application/json
```

Interactive IDEs such as GraphiQL or Apollo Studio work out of the box if you open `/graphql/` in a browser while `DEBUG=True`.

---

## 2. Schema Overview

```graphql
enum UserRole {
  ADMIN
  FREEMIUM_USER
}

input UserRegistrationInput {
  username: String!
  email: String!
  password: String!
  firstName: String
  lastName: String
  bio: String
  phoneNumber: String
  defaultLocation: String
  role: UserRole            # Optional – defaults to FREEMIUM_USER
}

type UserProfileType {
  id: ID!
  bio: String
  phoneNumber: String
  defaultLocation: String
  role: UserRole!
  profilePictureUrl: String
}

type UserType {
  id: ID!
  username: String!
  email: String!
  firstName: String
  lastName: String
  dateJoined: DateTime!
  isActive: Boolean!
  profile: UserProfileType!
}

type UserRegistrationResult {
  success: Boolean!
  message: String!
  user: UserType
}

type Query {
  # Returns the currently authenticated user
  me: UserType

  # ADMIN-only:
  user(id: ID!): UserType
  users(username: String, role: UserRole): [UserType!]
}

type Mutation {
  register(input: UserRegistrationInput!): UserRegistrationResult!
}
```

Field names in GraphQL are automatically camel-cased by Strawberry.  
If you use a different casing convention on the client, adjust the examples accordingly.

---

## 3. User Roles & Access Control

| Role            | Description                                                                                  | Default? |
|-----------------|----------------------------------------------------------------------------------------------|----------|
| `FREEMIUM_USER` | Regular user. Can register, log in, access own data (`me`), and operate on other public APIs | ✔        |
| `ADMIN`         | Elevated privileges. In addition to everything a freemium user can do, admins can query any user via the `user` and `users` queries. |          |

### 3.1 How Roles Are Assigned

* **During registration** – Include the `role` field in `UserRegistrationInput`. If omitted, the backend assigns `FREEMIUM_USER`.
* **After registration** – Promote/demote users via:
  * Django admin (`/admin/`) – edit `UserProfile.role`
  * Custom management command:  
    ```bash
    poetry run python manage.py create_admin --username alice --email alice@example.com --password 'S3cr3t!'
    ```
  * Utility helpers in `users/utils.py` (`promote_to_admin`, `demote_from_admin`, etc.)

### 3.2 Protected Queries

| Query         | Accessible By | Notes                                                                                       |
|---------------|---------------|---------------------------------------------------------------------------------------------|
| `me`          | Any authenticated user | Returns only the caller’s own data.                                                   |
| `user(id)`    | **ADMIN only** | Returns a single user by ID. Non-admin callers receive `null` with an “not authorized” error. |
| `users(...)`  | **ADMIN only** | Returns a list of users (optionally filtered). Non-admin callers receive an authorization error. |

The enforcement is implemented through a custom Strawberry `BasePermission` (`IsAdmin`) that checks `request.user.profile.role == 'admin'`.

Example error response for non-admin caller:

```json
{
  "errors": [
    {
      "message": "User is not authorized to access this resource",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["user"]
    }
  ],
  "data": { "user": null }
}
```

---

## 4. Registering a User

### 4.1 Example Mutation (GraphiQL)

```graphql
mutation RegisterUser($input: UserRegistrationInput!) {
  register(input: $input) {
    success
    message
    user {
      id
      username
      email
      profile {
        role
      }
    }
  }
}
```

#### Variables

```json
{
  "input": {
    "username": "jane_doe",
    "email": "jane@example.com",
    "password": "S3cr3tPassw0rd!",
    "firstName": "Jane",
    "lastName": "Doe",
    "role": "FREEMIUM_USER"
  }
}
```

If you omit `role`, **FREEMIUM_USER** is used automatically.

---

## 5. Querying the Current User (`me`)

After registration (or once you authenticate via session / token), you can query the logged-in user:

```graphql
query {
  me {
    id
    username
    email
    profile {
      role
    }
  }
}
```

---

## 6. Admin-only Queries

### 6.1 Get a User by ID

```graphql
query {
  user(id: 3) {
    username
    email
    profile {
      role
    }
  }
}
```

### 6.2 List All Users

```graphql
query {
  users(role: ADMIN) {
    id
    username
    email
  }
}
```

Both operations will fail for callers who are not admins.

---

## 7. Error Handling

`register`, `user`, and `users` return structured errors as shown above.  
HTTP status remains **200 OK**; use the presence of `errors` or the `success` flag to determine operation result.

---

## 8. Next Steps

* Implement token-based authentication for stateless clients.
* Add email verification & password reset.
* Extend role set if business needs evolve (e.g., `PREMIUM_USER`, `MODERATOR`, etc.).

For questions or issues, open an issue in the repository or contact the maintainers.
