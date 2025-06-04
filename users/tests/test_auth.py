import json
from django.test import TestCase
from django.urls import reverse

from users.models import User, UserRole


class JWTAuthenticationTests(TestCase):
    """
    Test suite for JWT authentication in the GraphQL API.
    Tests user registration, login, token refresh, protected endpoint access, and logout.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
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
        
        # GraphQL endpoint
        self.graphql_url = reverse('graphql')
        
        # Common GraphQL queries and mutations
        self.register_mutation = '''
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
        '''
        
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
        
        self.refresh_mutation = '''
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
        '''
        
        self.logout_mutation = '''
            mutation Logout($input: LogoutInput!) {
                logout(input: $input) {
                    success
                    message
                }
            }
        '''
        
        self.me_query = '''
            query {
                me {
                    id
                    username
                    email
                }
            }
        '''
        
        self.user_query = '''
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    username
                    email
                }
            }
        '''

    def execute_graphql(self, query, variables=None, headers=None):
        """
        Helper method to execute GraphQL queries and mutations.
        
        Args:
            query (str): The GraphQL query or mutation
            variables (dict, optional): Variables for the query
            headers (dict, optional): HTTP headers including authorization
            
        Returns:
            dict: The parsed JSON response
        """
        data = {
            'query': query,
            'variables': variables or {}
        }
        
        http_headers = {'Content-Type': 'application/json'}
        if headers:
            http_headers.update(headers)
            
        response = self.client.post(
            self.graphql_url,
            data=json.dumps(data),
            content_type='application/json',
            **({} if not headers else {'HTTP_' + k.upper().replace('-', '_'): v for k, v in headers.items()})
        )
        
        return json.loads(response.content)

    def test_user_registration(self):
        """Test user registration functionality."""
        # Test successful registration
        variables = {
            'input': {
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'newpassword123',
                'firstName': 'New',
                'lastName': 'User'
            }
        }
        
        response = self.execute_graphql(self.register_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('register', response['data'])
        self.assertTrue(response['data']['register']['success'])
        self.assertEqual(response['data']['register']['user']['username'], 'newuser')
        
        # Test registration with existing username
        variables['input']['email'] = 'another@example.com'
        response = self.execute_graphql(self.register_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('register', response['data'])
        self.assertFalse(response['data']['register']['success'])
        self.assertIn('Username already exists', response['data']['register']['message'])
        
        # Test registration with existing email
        variables['input']['username'] = 'anotheruser'
        variables['input']['email'] = 'test@example.com'
        response = self.execute_graphql(self.register_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('register', response['data'])
        self.assertFalse(response['data']['register']['success'])
        self.assertIn('Email already exists', response['data']['register']['message'])

    def test_user_login(self):
        """Test user login functionality with correct and incorrect credentials."""
        # Test successful login
        variables = {
            'input': {
                'username': 'testuser',
                'password': 'testpassword123'
            }
        }
        
        response = self.execute_graphql(self.login_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('login', response['data'])
        self.assertTrue(response['data']['login']['success'])
        self.assertIn('tokens', response['data']['login'])
        self.assertIn('access', response['data']['login']['tokens'])
        self.assertIn('refresh', response['data']['login']['tokens'])
        self.assertIn('token', response['data']['login']['tokens']['access'])
        self.assertIn('token', response['data']['login']['tokens']['refresh'])
        
        # Test login with incorrect username
        variables['input']['username'] = 'wronguser'
        response = self.execute_graphql(self.login_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('login', response['data'])
        self.assertFalse(response['data']['login']['success'])
        self.assertIn('Invalid username or password', response['data']['login']['message'])
        
        # Test login with incorrect password
        variables['input']['username'] = 'testuser'
        variables['input']['password'] = 'wrongpassword'
        response = self.execute_graphql(self.login_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('login', response['data'])
        self.assertFalse(response['data']['login']['success'])
        self.assertIn('Invalid username or password', response['data']['login']['message'])

    def test_token_refresh(self):
        """Test token refresh functionality."""
        # First, login to get tokens
        variables = {
            'input': {
                'username': 'testuser',
                'password': 'testpassword123'
            }
        }
        
        login_response = self.execute_graphql(self.login_mutation, variables)
        refresh_token = login_response['data']['login']['tokens']['refresh']['token']
        
        # Test successful token refresh
        variables = {
            'input': {
                'refreshToken': refresh_token
            }
        }
        
        response = self.execute_graphql(self.refresh_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('refreshToken', response['data'])
        self.assertTrue(response['data']['refreshToken']['success'])
        self.assertIn('tokens', response['data']['refreshToken'])
        self.assertIn('access', response['data']['refreshToken']['tokens'])
        self.assertIn('refresh', response['data']['refreshToken']['tokens'])
        
        # Test refresh with invalid token
        variables['input']['refreshToken'] = 'invalid.token.here'
        response = self.execute_graphql(self.refresh_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('refreshToken', response['data'])
        self.assertFalse(response['data']['refreshToken']['success'])
        self.assertIn('Token refresh failed', response['data']['refreshToken']['message'])

    def test_protected_endpoints(self):
        """Test accessing protected endpoints with and without valid tokens."""
        # First, login to get tokens
        variables = {
            'input': {
                'username': 'testuser',
                'password': 'testpassword123'
            }
        }
        
        login_response = self.execute_graphql(self.login_mutation, variables)
        access_token = login_response['data']['login']['tokens']['access']['token']
        
        # Test accessing 'me' endpoint with valid token
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.execute_graphql(self.me_query, headers=headers)
        
        self.assertIn('data', response)
        self.assertIn('me', response['data'])
        self.assertIsNotNone(response['data']['me'])
        self.assertEqual(response['data']['me']['username'], 'testuser')
        
        # Test accessing 'me' endpoint without token
        response = self.execute_graphql(self.me_query)
        
        self.assertIn('errors', response)
        self.assertIn('User is not authenticated', response['errors'][0]['message'])
        
        # Test accessing 'me' endpoint with invalid token
        headers = {'Authorization': 'Bearer invalid.token.here'}
        response = self.execute_graphql(self.me_query, headers=headers)
        
        self.assertIn('errors', response)
        self.assertIn('User is not authenticated', response['errors'][0]['message'])
        
        # Test accessing admin-only endpoint as regular user
        variables = {'id': str(self.admin_user.id)}
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.execute_graphql(self.user_query, variables, headers)
        
        self.assertIn('errors', response)
        self.assertIn('User is not authorized to access this resource', response['errors'][0]['message'])
        
        # Test accessing admin-only endpoint as admin
        admin_login_variables = {
            'input': {
                'username': 'adminuser',
                'password': 'adminpassword123'
            }
        }
        
        admin_login_response = self.execute_graphql(self.login_mutation, admin_login_variables)
        admin_access_token = admin_login_response['data']['login']['tokens']['access']['token']
        
        variables = {'id': str(self.test_user.id)}
        headers = {'Authorization': f'Bearer {admin_access_token}'}
        response = self.execute_graphql(self.user_query, variables, headers)
        
        self.assertIn('data', response)
        self.assertIn('user', response['data'])
        self.assertIsNotNone(response['data']['user'])
        self.assertEqual(response['data']['user']['username'], 'testuser')

    def test_logout(self):
        """Test logout functionality."""
        # First, login to get tokens
        variables = {
            'input': {
                'username': 'testuser',
                'password': 'testpassword123'
            }
        }
        
        login_response = self.execute_graphql(self.login_mutation, variables)
        access_token = login_response['data']['login']['tokens']['access']['token']
        refresh_token = login_response['data']['login']['tokens']['refresh']['token']
        
        # Test successful logout
        variables = {
            'input': {
                'refreshToken': refresh_token
            }
        }
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.execute_graphql(self.logout_mutation, variables, headers)
        
        self.assertIn('data', response)
        self.assertIn('logout', response['data'])
        self.assertTrue(response['data']['logout']['success'])
        
        # Verify the token is blacklisted by attempting to refresh it
        variables = {
            'input': {
                'refreshToken': refresh_token
            }
        }
        
        response = self.execute_graphql(self.refresh_mutation, variables)
        self.assertIn('data', response)
        self.assertIn('refreshToken', response['data'])
        self.assertFalse(response['data']['refreshToken']['success'])
        
        # Test logout with invalid token
        variables = {
            'input': {
                'refreshToken': 'invalid.token.here'
            }
        }
        
        response = self.execute_graphql(self.logout_mutation, variables)
        
        self.assertIn('data', response)
        self.assertIn('logout', response['data'])
        self.assertFalse(response['data']['logout']['success'])
        self.assertIn('Logout failed', response['data']['logout']['message'])
