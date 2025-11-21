#!/usr/bin/env python
"""
Script para importar usuarios a Postgres en Railway.
Ejecutar con: railway run python import_users_to_postgres.py
"""
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Leer usuarios del archivo JSON
input_file = 'users_export.json'

if not os.path.exists(input_file):
    print(f"❌ Archivo {input_file} no encontrado")
    print("   Primero ejecuta: python migrate_users_to_postgres.py (sin DATABASE_URL)")
    sys.exit(1)

print(f"📖 Leyendo usuarios de {input_file}...")

with open(input_file, 'r') as f:
    users_data = json.load(f)

print(f"📥 Importando {len(users_data)} usuario(s) a Postgres...")

imported = 0
updated = 0
skipped = 0

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
        
        print(f"  ✓ Usuario actualizado: {username} (superuser: {user.is_superuser})")
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
        
        print(f"  ✓ Usuario creado: {username} (superuser: {user.is_superuser})")
        imported += 1

print(f"\n✅ Importación completada:")
print(f"   - Creados: {imported}")
print(f"   - Actualizados: {updated}")
print(f"   - Total: {imported + updated}")

