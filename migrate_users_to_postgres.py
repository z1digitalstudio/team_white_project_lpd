#!/usr/bin/env python
"""
Script para migrar usuarios de SQLite local a Postgres en Railway.
Ejecutar con: python migrate_users_to_postgres.py
"""
import os
import sys
import django

# Configurar Django para usar SQLite local primero
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Si hay DATABASE_URL, la usamos (Postgres), si no, usamos SQLite
if os.environ.get('DATABASE_URL'):
    # Estamos en Postgres, necesitamos leer de SQLite
    print("⚠️  DATABASE_URL está configurada. Para leer de SQLite local, ejecuta sin DATABASE_URL")
    print("   Ejemplo: unset DATABASE_URL && python migrate_users_to_postgres.py")
    sys.exit(1)

# Configurar Django
django.setup()

from django.contrib.auth import get_user_model
import json

User = get_user_model()

print("📖 Leyendo usuarios de SQLite local...")

# Leer todos los usuarios de SQLite
users_data = []
for user in User.objects.all():
    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        'password': user.password,  # El hash de la contraseña
    }
    users_data.append(user_data)
    print(f"  ✓ Usuario encontrado: {user.username} (superuser: {user.is_superuser}, staff: {user.is_staff})")

if not users_data:
    print("❌ No se encontraron usuarios en SQLite local")
    sys.exit(1)

# Guardar en un archivo JSON
output_file = 'users_export.json'
with open(output_file, 'w') as f:
    json.dump(users_data, f, indent=2)

print(f"\n✅ {len(users_data)} usuario(s) exportado(s) a {output_file}")
print("\n📤 Para importar a Postgres en Railway, ejecuta:")
print(f"   railway run python import_users_to_postgres.py")
print("\nO copia el contenido de users_export.json y úsalo con el script de importación")

