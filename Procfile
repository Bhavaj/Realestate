release: python manage.py migrate && python manage.py setup_gifts && python manage.py createsu
web: gunicorn realestate_project.wsgi:application --bind 0.0.0.0:$PORT
