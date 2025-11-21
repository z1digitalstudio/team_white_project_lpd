"""
Management command to import users from users_export.json to Postgres.
Usage: python manage.py import_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import json
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Import users from users_export.json to Postgres'

    def handle(self, *args, **options):
        input_file = 'users_export.json'
        
        if not os.path.exists(input_file):
            # Silencioso - no mostrar error si el archivo no existe
            return

        with open(input_file, 'r') as f:
            users_data = json.load(f)

        imported = 0
        updated = 0

        for user_data in users_data:
            username = user_data['username']
            
            try:
                # Intentar obtener el usuario existente
                user = User.objects.get(username=username)
                
                # Actualizar el usuario existente
                user.email = user_data.get('email', '')
                user.first_name = user_data.get('first_name', '')
                user.last_name = user_data.get('last_name', '')
                user.is_staff = user_data.get('is_staff', False)
                user.is_superuser = user_data.get('is_superuser', False)
                user.is_active = user_data.get('is_active', True)
                user.password = user_data['password']  # Mantener el hash original
                user.save()
                updated += 1
                
            except User.DoesNotExist:
                # Crear nuevo usuario
                user = User.objects.create_user(
                    username=username,
                    email=user_data.get('email', ''),
                    password=None,  # No podemos usar create_user con hash, usamos create
                )
                
                # Actualizar campos adicionales
                user.first_name = user_data.get('first_name', '')
                user.last_name = user_data.get('last_name', '')
                user.is_staff = user_data.get('is_staff', False)
                user.is_superuser = user_data.get('is_superuser', False)
                user.is_active = user_data.get('is_active', True)
                user.password = user_data['password']  # Asignar el hash directamente
                user.save()
                imported += 1

        # Silencioso - no mostrar logs

