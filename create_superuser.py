#!/usr/bin/env python
"""
Script para crear un superusuario en Django.
Ejecutar con: python create_superuser.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    username = input('Username: ')
    email = input('Email: ')
    password = input('Password: ')
    
    if User.objects.filter(username=username).exists():
        print(f'User {username} already exists!')
        return
    
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully!')

if __name__ == '__main__':
    create_superuser()

