#!/bin/bash

echo "🚀 Starting Railway deployment..."

# Test database connection
echo "⏳ Testing database connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
django.setup()

from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Run migrations
echo "📊 Running migrations..."
python manage.py migrate

# Setup gifts
echo "🎁 Setting up gifts..."
python manage.py setup_gifts

# Create superuser
echo "👤 Creating admin user..."
python manage.py createsu

# Start server
echo "🎉 Starting web server..."
exec gunicorn realestate_project.wsgi:application --bind 0.0.0.0:$PORT
