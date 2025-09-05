#!/usr/bin/env python
"""
Railway startup script to automatically run migrations and setup gifts
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
    django.setup()
    
    print("🚀 Starting Railway deployment setup...")
    
    try:
        # Run migrations
        print("📊 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
        
        # Setup gifts (this will only create gifts if they don't exist)
        print("🎁 Setting up gift system...")
        execute_from_command_line(['manage.py', 'setup_gifts'])
        print("✅ Gift system setup completed!")
        
        print("🎉 Railway setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        # Don't exit with error, let the app continue
        pass

if __name__ == '__main__':
    main()
