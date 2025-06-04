"""
Tests for the login functionality in the auth_api app.

This module contains tests for the JWT-based authentication system,
specifically focusing on the login mutation and token validation.
"""
from django.test import TestCase

from users.tests.utils import GraphQLTestClient, GraphQLResponse
from users.models import UserRole, User


class LoginMutationTests(TestCase):
    """Test suite for the login mutation."""
    
    def setUp(self):
        """Set up test data."""
        # Create a regular test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )
        self.admin_user.role = UserRole.ADMIN
        self.admin_user.save()
        
        # Create an inactive user
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='inactivepassword123',
            is_active=False
        )
        
        # Initialize the GraphQL client
        self.client = GraphQLTestClient()
        
        # Login mutation
        self.login_mutation = '''
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
                    }
                }
            }
        '''
    
    def test_successful_login(self):
        """Test successful login with valid credentials."""
        variables = {
            'input': {
                'username': 'testuser',
                'password': 'testpassword123'
            }
        }
        
        response = GraphQLResponse(self.client.mutate(self.login_mutation, variables))
        
        # Check the response structure
        self.assertFalse(response.has_errors)
        self.assertTrue(response.get_field_value('login.success'))
        self.assertEqual(response.get_field_value('login.message'), 'Login successful')
        
        # Check that tokens are present
        self.assertIsNotNone(response.get_field_value('login.tokens.access.token'))
        self.assertIsNotNone(response.get_field_value('login.tokens.refresh.token'))
        
        # Check user information
        self.assertEqual(response.get_field_value('login.user.username'), 'testuser')
    
    def  test_admin_login(self):
        """Test successful login as admin user."""
        variables = {
            'input': {
                'username': 'adminuser',
                'password': 'adminpassword123'
            }
        }
        
        response = GraphQLResponse(self.client.mutate(self.login_mutation, variables))
        
        # Check the response structure
        self.assertFalse(response.has_errors)
        self.assertTrue(response.get_field_value('login.success'))
        
        # Authenticate with the received token
        self.client.access_token = response.get_field_value('login.tokens.access.token')
        
        # Test admin-only query
        admin_query = '''
            query {
                users {
                    id
                    username
                }
            }
        '''
        
        admin_response = GraphQLResponse(self.client.query(admin_query))
        # Admin should be able to access the users query
        self.assertFalse(admin_response.has_errors)
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Test with invalid username
        variables = {
            'input': {
                'username': 'nonexistentuser',
                'password': 'testpassword123'
            }
        }
        
        response = GraphQLResponse(self.client.mutate(self.login_mutation, variables))
        
        self.assertFalse(response.has_errors)  # GraphQL operation succeeds but login fails
        self.assertFalse(response.get_field_value('login.success'))
        self.assertEqual(response.get_field_value('login.message'), 'Invalid username or password')
        self.assertIsNone(response.get_field_value('login.tokens'))
        
        # Test with invalid password
        variables = {
            'input': {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
        }
        
        response = GraphQLResponse(self.client.mutate(self.login_mutation, variables))
        
        self.assertFalse(response.has_errors)
        self.assertFalse(response.get_field_value('login.success'))
        self.assertEqual(response.get_field_value('login.message'), 'Invalid username or password')
        self.assertIsNone(response.get_field_value('login.tokens'))
    
    def test_inactive_user(self):
        """Test login with an inactive user account."""
        variables = {
            'input': {
                'username': 'inactiveuser',
                'password': 'inactivepassword123'
            }
        }
        
        response = GraphQLResponse(self.client.mutate(self.login_mutation, variables))
        
        self.assertFalse(response.has_errors)
        self.assertFalse(response.get_field_value('login.success'))
        self.assertEqual(response.get_field_value('login.message'), 'Invalid username or password')
        self.assertIsNone(response.get_field_value('login.tokens'))
    
    def test_token_usage(self):
        """Test using the token to access protected endpoints."""
        # First login to get a token
        variables = {
            'input': {
                'username': 'testuser',
                'password': 'testpassword123'
            }
        }
        
        login_response = GraphQLResponse(self.client.mutate(self.login_mutation, variables))
        self.client.access_token = login_response.get_field_value('login.tokens.access.token')
        
        # Try to access the me query with the token
        me_query = '''
            query {
                me {
                    id
                    username
                    email
                }
            }
        '''
        
        me_response = GraphQLResponse(self.client.query(me_query))
        
        # Should succeed with valid token
        self.assertFalse(me_response.has_errors)
        self.assertEqual(me_response.get_field_value('me.username'), 'testuser')
        
        # Clear authentication and try again
        self.client.clear_authentication()
        me_response = GraphQLResponse(self.client.query(me_query))
        
        # Should fail without token
        self.assertTrue(me_response.has_errors)
        self.assertIn('User is not authenticated', me_response.get_first_error_message())
