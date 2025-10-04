#!/usr/bin/env python
"""
Simple script to test admin user creation
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

print("🔍 Testing admin user...")

# Check if admin user exists
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"✅ Admin user exists: {admin_user.username}")
    print(f"   Email: {admin_user.email}")
    print(f"   Is staff: {admin_user.is_staff}")
    print(f"   Is superuser: {admin_user.is_superuser}")
    
    # Test authentication
    test_user = authenticate(username='admin', password='adminpass')
    if test_user:
        print("✅ Admin login test: SUCCESS")
    else:
        print("❌ Admin login test: FAILED")
else:
    print("❌ Admin user does not exist")
    
    # Try to create admin user
    print("🔧 Creating admin user...")
    try:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        print("✅ Admin user created successfully!")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

print("📊 Total users in database:", User.objects.count())
