from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import getpass
import sys

from users.utils import create_admin_user


class Command(BaseCommand):
    help = 'Creates a new admin user with the specified credentials'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the admin user')
        parser.add_argument('--email', type=str, help='Email address for the admin user')
        parser.add_argument('--password', type=str, help='Password for the admin user (if not provided, will prompt)')
        parser.add_argument('--first-name', type=str, help='First name for the admin user', default='')
        parser.add_argument('--last-name', type=str, help='Last name for the admin user', default='')
        parser.add_argument('--no-input', action='store_true', help='Run command without interactive prompts')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        no_input = options['no_input']

        # Interactive mode if no_input is False
        if not no_input:
            # Get username if not provided
            if not username:
                username = input('Username: ')
            
            # Get email if not provided
            if not email:
                email = input('Email address: ')
            
            # Get password if not provided (without echoing)
            if not password:
                password = getpass.getpass('Password: ')
                password_confirm = getpass.getpass('Password (again): ')
                
                if password != password_confirm:
                    self.stderr.write(self.style.ERROR('Error: Passwords do not match'))
                    sys.exit(1)
            
            # Get optional first name if not provided
            if not first_name and input('Do you want to add a first name? (y/n): ').lower() == 'y':
                first_name = input('First name: ')
            
            # Get optional last name if not provided
            if not last_name and input('Do you want to add a last name? (y/n): ').lower() == 'y':
                last_name = input('Last name: ')
        
        # Validate required fields
        if not username:
            raise CommandError('Username is required')
        
        if not email:
            raise CommandError('Email address is required')
        
        if not password:
            raise CommandError('Password is required')
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise CommandError(f'Password validation failed: {", ".join(e.messages)}')
        
        # Create the admin user
        user, success, message = create_admin_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'Success: {message}'))
            self.stdout.write(f'Admin user "{username}" created with ID: {user.id}')
        else:
            self.stderr.write(self.style.ERROR(f'Error: {message}'))
            sys.exit(1)
