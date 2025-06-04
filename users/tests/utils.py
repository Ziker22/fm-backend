"""
Test utilities for GraphQL API testing.

This module provides helper classes and functions for testing GraphQL APIs,
including a GraphQLTestClient that simplifies executing GraphQL operations
in tests and handling authentication.
"""
import json
from typing import Dict, Any, Optional, Union

from django.test.client import Client
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class GraphQLTestClient:
    """
    Test client for GraphQL API testing.
    
    This client wraps Django's test client and provides methods for executing
    GraphQL queries and mutations with proper context setup and authentication.
    
    Example:
        client = GraphQLTestClient()
        
        # Execute a query
        response = client.query('''
            query {
                me {
                    id
                    username
                }
            }
        ''')
        
        # Execute a mutation with variables
        response = client.mutate(
            '''
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    success
                    tokens {
                        access { token }
                    }
                }
            }
            ''',
            variables={'input': {'username': 'test', 'password': 'test'}}
        )
        
        # Execute with authentication
        client.authenticate(user)
        response = client.query('query { me { id } }')
    """
    
    def __init__(self, endpoint: str = 'graphql'):
        """
        Initialize the GraphQL test client.
        
        Args:
            endpoint: The GraphQL endpoint path (default: 'graphql')
        """
        self.client = Client()
        self.endpoint = reverse(endpoint)
        self.access_token = None
    
    def authenticate(self, user: User) -> None:
        """
        Authenticate the client with a user.
        
        This method generates a JWT token for the user and sets it up for
        subsequent requests.
        
        Args:
            user: The user to authenticate as
        """
        refresh = RefreshToken.for_user(user)
        self.access_token = str(refresh.access_token)
    
    def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query: The GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            Dict containing the parsed GraphQL response
        """
        return self._execute(query, variables)
    
    def mutate(self, mutation: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL mutation.
        
        Args:
            mutation: The GraphQL mutation string
            variables: Optional variables for the mutation
            
        Returns:
            Dict containing the parsed GraphQL response
        """
        return self._execute(mutation, variables)
    
    def _execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL operation (query or mutation).
        
        Args:
            query: The GraphQL operation string
            variables: Optional variables for the operation
            
        Returns:
            Dict containing the parsed GraphQL response
        """
        data = {
            'query': query,
            'variables': variables or {}
        }
        
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Convert headers to Django test client format
        django_headers = {
            f'HTTP_{key.upper().replace("-", "_")}': value
            for key, value in headers.items()
        }
        
        response = self.client.post(
            self.endpoint,
            data=json.dumps(data),
            content_type='application/json',
            **django_headers
        )
        
        return json.loads(response.content)
    
    def clear_authentication(self) -> None:
        """Clear the current authentication."""
        self.access_token = None
    
    def get_token_for_user(self, user: User) -> Dict[str, str]:
        """
        Generate access and refresh tokens for a user.
        
        Args:
            user: The user to generate tokens for
            
        Returns:
            Dict containing access and refresh tokens
        """
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class GraphQLResponse:
    """
    Helper class for working with GraphQL responses.
    
    This class provides a more convenient way to access GraphQL response data
    and check for errors.
    
    Example:
        response = GraphQLResponse(client.query('query { me { id } }'))
        
        if response.has_errors:
            print(response.errors)
        else:
            user_id = response.data['me']['id']
    """
    
    def __init__(self, response_data: Dict[str, Any]):
        """
        Initialize with GraphQL response data.
        
        Args:
            response_data: The parsed GraphQL response
        """
        self.response = response_data
        self.data = response_data.get('data')
        self.errors = response_data.get('errors', [])
    
    @property
    def has_errors(self) -> bool:
        """Check if the response has any errors."""
        return len(self.errors) > 0
    
    def get_field_value(self, path: str) -> Any:
        """
        Get a value from the response data using a dot-notation path.
        
        Args:
            path: The path to the value (e.g., 'user.profile.role')
            
        Returns:
            The value at the specified path or None if not found
        """
        if not self.data:
            return None
        
        current = self.data
        for part in path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def get_first_error_message(self) -> Optional[str]:
        """Get the message from the first error, if any."""
        if self.errors and 'message' in self.errors[0]:
            return self.errors[0]['message']
        return None
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access to the response data."""
        return self.response[key]
