import strawberry
from strawberry.tools import merge_types
from typing import Optional, List

# Import schemas from apps
from users.schema import Query as UsersQuery
from users.schema import Mutation as UsersMutation

# Merge queries from all apps
Query = merge_types("Query", (UsersQuery,))

# Merge mutations from all apps
Mutation = merge_types("Mutation", (UsersMutation,))

# Create the main schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
