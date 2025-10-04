from django.core.management.base import BaseCommand
import json
from django.db import transaction

class Command(BaseCommand):
    help = 'Import data from Render export file'

    def add_arguments(self, parser):
        parser.add_argument('export_file', type=str, nargs='?', default='data_export/render_data_export_20251003_192946.json', help='Path to the export file')

    def handle(self, *args, **options):
        """Import data from export file - only if database is empty"""
        
        from realestate.models import Agent, Customer, Payment, Project, Gift, AgentGift
        
        # Check if database already has data
        total_records = (
            Agent.objects.count() + 
            Customer.objects.count() + 
            Project.objects.count() + 
            Payment.objects.count() + 
            AgentGift.objects.count()
        )
        
        if total_records > 0:
            self.stdout.write(self.style.WARNING("⚠️  Database already contains data. Skipping import to prevent data loss."))
            self.stdout.write(f"📊 Current data: Agents={Agent.objects.count()}, Customers={Customer.objects.count()}, Projects={Project.objects.count()}, Payments={Payment.objects.count()}, Agent Gifts={AgentGift.objects.count()}")
            return
        
        export_file = options['export_file']
        
        try:
            with open(export_file, 'r') as f:
                export_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ Export file not found: {export_file}"))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"❌ Invalid JSON file: {e}"))
            return
        
        from django.core import serializers
        
        self.stdout.write("🔄 Starting initial data import from Render...")
        self.stdout.write("ℹ️  This will only run once when database is empty.")
        
        # Import in correct order (respecting foreign key dependencies)
        import_order = [
            ('gifts', Gift),
            ('projects', Project),
            ('agents', Agent),
            ('customers', Customer),
            ('payments', Payment),
            ('agent_gifts', AgentGift),
        ]
        
        with transaction.atomic():
            for model_name, model_class in import_order:
                if model_name in export_data and export_data[model_name]:
                    try:
                        # Deserialize and save objects
                        serialized_data = json.dumps(export_data[model_name])
                        objects = serializers.deserialize('json', serialized_data)
                        
                        count = 0
                        for obj in objects:
                            obj.save()
                            count += 1
                        
                        self.stdout.write(self.style.SUCCESS(f"✅ Imported {count} {model_name}"))
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Error importing {model_name}: {e}"))
                        # Continue with other models
        
        self.stdout.write("🎉 Initial data import completed successfully!")
        
        # Verify import
        self.stdout.write("🔍 Verifying import...")
        self.stdout.write(f"Agents: {Agent.objects.count()}")
        self.stdout.write(f"Customers: {Customer.objects.count()}")
        self.stdout.write(f"Projects: {Project.objects.count()}")
        self.stdout.write(f"Payments: {Payment.objects.count()}")
        self.stdout.write(f"Gifts: {Gift.objects.count()}")
        self.stdout.write(f"Agent Gifts: {AgentGift.objects.count()}")
