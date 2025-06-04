import strawberry
from strawberry.tools import merge_types

# Import schemas from apps
from users.schema import Query as UsersQuery
from users.schema import Mutation as UsersMutation
from auth_api.graphql.schema import Query as AuthQuery
from auth_api.graphql.schema import Mutation as AuthMutation

# Merge queries from all apps
Query = merge_types("Query", (UsersQuery, AuthQuery))

# Merge mutations from all apps
Mutation = merge_types("Mutation", (UsersMutation, AuthMutation))

# Create the main schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation

)
