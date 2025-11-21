"""
Management command to create or update a superuser.
If user exists, updates password. If not, creates new superuser.

Usage:
    python manage.py create_or_update_superuser --username admin --email admin@example.com --password secret
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update a superuser'

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

        if not password:
            self.stdout.write(
                self.style.ERROR('Error: Password is required.')
            )
            return

        # Check if user already exists
        try:
            user = User.objects.get(username=username)
            # User exists, update password and ensure is_staff and is_superuser
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated superuser "{username}" with new password')
            )
        except User.DoesNotExist:
            # User doesn't exist, create new superuser
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

