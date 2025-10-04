#!/usr/bin/env python
"""
Railway startup script to run migrations and setup commands
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run startup commands for Railway deployment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
    django.setup()
    
    print("🚀 Starting Railway deployment setup...")
    
    try:
        # Run migrations
        print("📊 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
        
        # Setup default gifts
        print("🎁 Setting up default gifts...")
        execute_from_command_line(['manage.py', 'setup_gifts'])
        print("✅ Default gifts setup completed!")
        
        # Create superuser if it doesn't exist
        print("👤 Creating admin superuser...")
        execute_from_command_line(['manage.py', 'createsu'])
        print("✅ Admin superuser setup completed!")
        
        print("🎉 Railway deployment setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()