from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create or update admin user'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpass')
        
        self.stdout.write(f"🔍 Looking for admin user: {username}")
        
        try:
            # Check if user exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(f"✅ Admin user '{username}' already exists")
                
                # Update password to ensure it's correct
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(f"✅ Updated password for admin user '{username}'")
                
            else:
                # Create new user
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(f"✅ Created new admin user '{username}'")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating admin user: {e}"))
            return
        
        # Test login
        try:
            from django.contrib.auth import authenticate
            test_user = authenticate(username=username, password=password)
            if test_user:
                self.stdout.write(f"✅ Admin login test successful!")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Admin login test failed!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Login test error: {e}"))
