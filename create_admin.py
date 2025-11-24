#!/usr/bin/env python
"""
Script to create or update the admin superuser.
Run with: railway run python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@z1.digital'
password = 'z1digital'

User.objects.filter(username='adm').delete()
User.objects.filter(username=username).delete()

user = User.objects.create_superuser(
    username=username,
    email=email,
    password=password
)


