# User Registration via GraphQL

This document describes how to register a new user in the Family-Map backend using the GraphQL API powered by Strawberry-Django.

---

## 1. GraphQL Endpoint

```
POST /graphql/
Content-Type: application/json
```

The endpoint accepts standard GraphQL POST bodies:

```json
{
  "query": "...",
  "variables": { ... }
}
```

Interactive IDEs such as GraphiQL or Apollo Studio work out of the box if you open `/graphql/` in a browser while `DEBUG=True`.

---

## 2. Schema Overview

```graphql
input UserRegistrationInput {
  username: String!
  email: String!
  password: String!
  firstName: String
  lastName: String
  bio: String
  phoneNumber: String
  defaultLocation: String
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

type Mutation {
  register(input: UserRegistrationInput!): UserRegistrationResult!
}
```

*Field names in GraphQL are automatically camel-cased by Strawberry.  
If you use a different casing convention on the client, adjust the examples accordingly.*

---

## 3. Registering a User

### 3.1 Example Mutation (GraphiQL)

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
        bio
        phoneNumber
        defaultLocation
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
    "bio": "Mother of two, loves playground scouting",
    "phoneNumber": "+123456789",
    "defaultLocation": "San Francisco, CA"
  }
}
```

#### Expected Successful Response

```json
{
  "data": {
    "register": {
      "success": true,
      "message": "User registered successfully",
      "user": {
        "id": "1",
        "username": "jane_doe",
        "email": "jane@example.com",
        "profile": {
          "bio": "Mother of two, loves playground scouting",
          "phoneNumber": "+123456789",
          "defaultLocation": "San Francisco, CA"
        }
      }
    }
  }
}
```

### 3.2 cURL Example

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation Register($input: UserRegistrationInput!) { register(input: $input) { success message } }","variables":{"input":{"username":"john","email":"john@example.com","password":"Top$ecret123"}}}'
```

---

## 4. Querying the Current User (`me`)

After registration (or once you authenticate via session / token), you can query the logged-in user:

```graphql
query {
  me {
    id
    username
    email
    profile {
      phoneNumber
    }
  }
}
```

When using token-based auth (e.g., `Authorization: Bearer <token>`), attach the header to your request.  
Session cookies work transparently with GraphiQL when you’re logged in via `/admin/`.

---

## 5. Error Handling

`register` always returns `success: false` with a descriptive `message` when something goes wrong:

| Message example                    | Cause                                   |
|------------------------------------|-----------------------------------------|
| `Username already exists`          | A user with the given username exists.  |
| `Email already exists`             | A user with the given email exists.     |
| `Registration failed: <details>`   | Unexpected server-side error.           |

HTTP status remains **200 OK**; use the `success` flag to determine operation result.

---

## 6. Next Steps

* Implement login & token issuance (e.g., `django-rest-knox` or `django-allauth`) if your frontend needs stateless auth.  
* Extend `UserProfile` with additional fields – Strawberry automatically exposes new fields when you regenerate the schema.

For questions or issues, open an issue in the repository or contact the maintainers.
