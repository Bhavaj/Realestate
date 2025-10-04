#!/bin/bash

# Railway startup script
echo "🚀 Starting Railway deployment..."

# Run setup command (includes migrations, gifts, superuser, and data import)
echo "🔧 Running Railway setup..."
python manage.py setup_railway

# Start the application
echo "🎉 Starting Django application..."
exec gunicorn realestate_project.wsgi:application --bind 0.0.0.0:$PORT
