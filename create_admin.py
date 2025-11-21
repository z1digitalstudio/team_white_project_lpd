#!/usr/bin/env python
"""
Script para crear o actualizar el superusuario admin.
Ejecutar con: railway run python create_admin.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@z1.digital'
password = 'z1digital'

# Eliminar usuario 'adm' si existe
User.objects.filter(username='adm').delete()
print(f"Usuario 'adm' eliminado si existía")

# Eliminar usuario 'admin' si existe (para recrearlo con nueva contraseña)
User.objects.filter(username=username).delete()
print(f"Usuario '{username}' eliminado si existía")

# Crear nuevo superusuario
user = User.objects.create_superuser(
    username=username,
    email=email,
    password=password
)
print(f"✅ Superusuario '{username}' creado exitosamente!")
print(f"   Email: {email}")
print(f"   Password: {password}")

