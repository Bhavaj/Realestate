#!/bin/bash

# Railway startup script
echo "🚀 Starting Railway deployment..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import os
import time
import django
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
django.setup()

max_attempts = 30
for attempt in range(max_attempts):
    try:
        connection.ensure_connection()
        print('✅ Database connection established!')
        break
    except Exception as e:
        print(f'⏳ Attempt {attempt + 1}/{max_attempts}: Waiting for database...')
        time.sleep(2)
else:
    print('❌ Could not connect to database after 60 seconds')
    exit(1)
"

# Run migrations
echo "📊 Running database migrations..."
python manage.py migrate

# Setup default gifts
echo "🎁 Setting up default gifts..."
python manage.py setup_gifts

# Create superuser
echo "👤 Creating admin superuser..."
python manage.py createsu

# Import data if available
if [ -f "render_data_export.json" ]; then
    echo "📥 Importing data from Render..."
    python manage.py import_railway_data render_data_export.json
fi

# Start the application
echo "🎉 Starting Django application..."
exec gunicorn realestate_project.wsgi:application --bind 0.0.0.0:$PORT
