#!/usr/bin/env python
"""
JWT Authentication Flow Example for Family Map Backend

This script demonstrates the complete JWT authentication flow:
1. Register a new user
2. Login to get access and refresh tokens
3. Access a protected endpoint (me query)
4. Refresh the tokens
5. Logout

Usage:
    python jwt_example.py [host]

    host: Optional API host (default: http://localhost:8000)

Requirements:
    pip install requests
"""
import argparse
import json
import random
import string
import sys
import time
from typing import Dict, Any, Optional

import requests


class FamilyMapClient:
    """Client for interacting with the Family Map GraphQL API with JWT authentication."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client with the API base URL.
        
        Args:
            base_url: Base URL of the Family Map API
        """
        self.base_url = base_url
        self.graphql_url = f"{base_url}/graphql/"
        self.access_token = None
        self.refresh_token = None
        self.username = None
    
    def execute_graphql(self, query: str, variables: Optional[Dict[str, Any]] = None, 
                        auth: bool = False) -> Dict[str, Any]:
        """
        Execute a GraphQL query or mutation.
        
        Args:
            query: GraphQL query or mutation string
            variables: Variables for the query
            auth: Whether to include the Authorization header
            
        Returns:
            Dict containing the GraphQL response
        """
        headers = {"Content-Type": "application/json"}
        
        if auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        data = {
            "query": query,
            "variables": variables or {}
        }
        
        response = requests.post(
            self.graphql_url,
            headers=headers,
            json=data
        )
        
        if not response.ok:
            print(f"HTTP Error: {response.status_code}")
            print(response.text)
            return {"errors": [{"message": f"HTTP Error: {response.status_code}"}]}
        
        return response.json()
    
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Username for the new user
            email: Email address for the new user
            password: Password for the new user
            
        Returns:
            Dict containing the registration result
        """
        mutation = """
        mutation Register($input: UserRegistrationInput!) {
            register(input: $input) {
                success
                message
                user {
                    id
                    username
                    email
                }
            }
        }
        """
        
        variables = {
            "input": {
                "username": username,
                "email": email,
                "password": password,
                "firstName": "Test",
                "lastName": "User"
            }
        }
        
        result = self.execute_graphql(mutation, variables)
        
        if result.get("data", {}).get("register", {}).get("success"):
            self.username = username
        
        return result
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and get JWT tokens.
        
        Args:
            username: Username to login with
            password: Password to login with
            
        Returns:
            Dict containing the login result
        """
        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                success
                message
                tokens {
                    access { token }
                    refresh { token }
                }
                user {
                    id
                    username
                    profile {
                        role
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "username": username,
                "password": password
            }
        }
        
        result = self.execute_graphql(mutation, variables)
        
        if result.get("data", {}).get("login", {}).get("success"):
            tokens = result["data"]["login"]["tokens"]
            self.access_token = tokens["access"]["token"]
            self.refresh_token = tokens["refresh"]["token"]
            self.username = username
        
        return result
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get the current user's information (protected endpoint).
        
        Returns:
            Dict containing the user information
        """
        query = """
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
        """
        
        return self.execute_graphql(query, auth=True)
    
    def refresh_tokens(self) -> Dict[str, Any]:
        """
        Refresh the access and refresh tokens.
        
        Returns:
            Dict containing the refresh result
        """
        mutation = """
        mutation RefreshToken($input: RefreshTokenInput!) {
            refreshToken(input: $input) {
                success
                message
                tokens {
                    access { token }
                    refresh { token }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "refreshToken": self.refresh_token
            }
        }
        
        result = self.execute_graphql(mutation, variables)
        
        if result.get("data", {}).get("refreshToken", {}).get("success"):
            tokens = result["data"]["refreshToken"]["tokens"]
            self.access_token = tokens["access"]["token"]
            self.refresh_token = tokens["refresh"]["token"]
        
        return result
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout by blacklisting the refresh token.
        
        Returns:
            Dict containing the logout result
        """
        mutation = """
        mutation Logout($input: LogoutInput!) {
            logout(input: $input) {
                success
                message
            }
        }
        """
        
        variables = {
            "input": {
                "refreshToken": self.refresh_token
            }
        }
        
        result = self.execute_graphql(mutation, variables, auth=True)
        
        if result.get("data", {}).get("logout", {}).get("success"):
            self.access_token = None
            self.refresh_token = None
        
        return result


def generate_random_credentials():
    """Generate random username, email and password for testing."""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    username = f"test_user_{random_str}"
    email = f"test_{random_str}@example.com"
    password = f"Password{random_str}!"
    
    return username, email, password


def print_section(title):
    """Print a section header for better readability."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50)


def print_result(result):
    """Print a GraphQL result in a readable format."""
    print(json.dumps(result, indent=2))


def main():
    """Run the JWT authentication flow demonstration."""
    parser = argparse.ArgumentParser(description="JWT Authentication Flow Example")
    parser.add_argument("host", nargs="?", default="http://localhost:8000", 
                        help="API host (default: http://localhost:8000)")
    args = parser.parse_args()
    
    client = FamilyMapClient(args.host)
    
    # Generate random credentials for testing
    username, email, password = generate_random_credentials()
    
    try:
        # Step 1: Register a new user
        print_section("1. Register a new user")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
        register_result = client.register_user(username, email, password)
        print_result(register_result)
        
        if not register_result.get("data", {}).get("register", {}).get("success"):
            print("Registration failed. Exiting.")
            return 1
        
        # Step 2: Login to get tokens
        print_section("2. Login to get tokens")
        login_result = client.login(username, password)
        print_result(login_result)
        
        if not login_result.get("data", {}).get("login", {}).get("success"):
            print("Login failed. Exiting.")
            return 1
        
        # Step 3: Access a protected endpoint
        print_section("3. Access a protected endpoint (me query)")
        me_result = client.get_me()
        print_result(me_result)
        
        # Step 4: Refresh the tokens
        print_section("4. Refresh the tokens")
        print("Waiting 2 seconds before refreshing tokens...")
        time.sleep(2)  # Wait a bit to ensure token timestamps differ
        
        refresh_result = client.refresh_tokens()
        print_result(refresh_result)
        
        if not refresh_result.get("data", {}).get("refreshToken", {}).get("success"):
            print("Token refresh failed. Exiting.")
            return 1
        
        # Verify the new token works
        print("\nVerifying the new token with another me query:")
        me_result_after_refresh = client.get_me()
        print_result(me_result_after_refresh)
        
        # Step 5: Logout
        print_section("5. Logout")
        logout_result = client.logout()
        print_result(logout_result)
        
        # Verify logout worked by trying to use the token again
        print("\nVerifying logout by trying to use the token again:")
        me_result_after_logout = client.get_me()
        print_result(me_result_after_logout)
        
        # Try to refresh the blacklisted token
        print("\nTrying to refresh the blacklisted token:")
        refresh_after_logout = client.refresh_tokens()
        print_result(refresh_after_logout)
        
        print("\nJWT authentication flow demonstration completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
