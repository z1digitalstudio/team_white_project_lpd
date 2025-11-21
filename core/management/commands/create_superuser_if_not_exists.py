"""
Management command to create a superuser if it doesn't exist.
Can be used with environment variables for automation.

Usage:
    python manage.py create_superuser_if_not_exists
    python manage.py create_superuser_if_not_exists --username admin --email admin@example.com --password secret
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser if it doesn\'t exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
            default=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser',
            default=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser',
            default=os.environ.get('DJANGO_SUPERUSER_PASSWORD', None)
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Use environment variables only (no prompts)',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        noinput = options['noinput']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Skipping.')
            )
            return

        # If no password provided and not in noinput mode, prompt
        if not password and not noinput:
            from getpass import getpass
            password = getpass('Password: ')
            password_again = getpass('Password (again): ')
            if password != password_again:
                self.stdout.write(
                    self.style.ERROR('Error: Passwords do not match.')
                )
                return

        # If still no password, generate a random one
        if not password:
            import secrets
            password = secrets.token_urlsafe(16)
            self.stdout.write(
                self.style.WARNING(f'No password provided. Generated random password: {password}')
            )

        # Create superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser "{username}"')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )

