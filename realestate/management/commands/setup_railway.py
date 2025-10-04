from django.core.management.base import BaseCommand
import os
import json

class Command(BaseCommand):
    help = 'Setup Railway deployment with migrations and data import'

    def handle(self, *args, **options):
        """Setup Railway deployment"""
        
        self.stdout.write("🚀 Setting up Railway deployment...")
        
        # Run migrations
        self.stdout.write("📊 Running database migrations...")
        from django.core.management import call_command
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS("✅ Migrations completed!"))
        
        # Setup default gifts
        self.stdout.write("🎁 Setting up default gifts...")
        call_command('setup_gifts')
        self.stdout.write(self.style.SUCCESS("✅ Default gifts setup completed!"))
        
        # Create superuser
        self.stdout.write("👤 Creating admin superuser...")
        call_command('createsu')
        self.stdout.write(self.style.SUCCESS("✅ Admin superuser setup completed!"))
        
        # Try to import data if export file exists
        export_files = [
            "render_data_export.json",
            "data_export/render_data_export_20251003_192946.json",
            "data_export/render_data_export.json"
        ]
        
        export_file = None
        for file_path in export_files:
            if os.path.exists(file_path):
                export_file = file_path
                break
        
        if export_file:
            self.stdout.write(f"📥 Importing data from {export_file}...")
            try:
                call_command('import_railway_data', export_file)
                self.stdout.write(self.style.SUCCESS("✅ Data import completed!"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Data import failed: {e}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  No export file found, skipping data import"))
        
        self.stdout.write(self.style.SUCCESS("🎉 Railway setup completed successfully!"))
