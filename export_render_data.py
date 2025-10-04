#!/usr/bin/env python
"""
Script to export data from Render PostgreSQL database
Run this locally with your Render database connection
"""
import os
import django
from django.core.management import execute_from_command_line
import json
from datetime import datetime

def export_data():
    """Export all data from the current database"""
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
    django.setup()
    
    from django.core import serializers
    from realestate.models import Agent, Customer, Payment, Project, Gift, AgentGift
    
    print("🔄 Starting data export from Render...")
    
    # Create export directory
    export_dir = "data_export"
    os.makedirs(export_dir, exist_ok=True)
    
    # Export each model
    models_to_export = [
        ('agents', Agent),
        ('customers', Customer),
        ('projects', Project),
        ('payments', Payment),
        ('gifts', Gift),
        ('agent_gifts', AgentGift),
    ]
    
    export_data = {}
    
    for model_name, model_class in models_to_export:
        try:
            # Get all objects
            objects = model_class.objects.all()
            count = objects.count()
            
            if count > 0:
                # Serialize to JSON
                data = serializers.serialize('json', objects)
                export_data[model_name] = json.loads(data)
                print(f"✅ Exported {count} {model_name}")
            else:
                export_data[model_name] = []
                print(f"ℹ️  No {model_name} to export")
                
        except Exception as e:
            print(f"❌ Error exporting {model_name}: {e}")
            export_data[model_name] = []
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{export_dir}/render_data_export_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"💾 Data exported to: {filename}")
    
    # Also create a SQL dump (backup method)
    print("📊 Creating SQL dump backup...")
    sql_filename = f"{export_dir}/render_data_backup_{timestamp}.sql"
    
    # This will create a SQL dump file
    os.system(f'python manage.py dumpdata --natural-foreign --natural-primary > {sql_filename}')
    
    print(f"💾 SQL backup created: {sql_filename}")
    print("🎉 Export completed successfully!")
    
    return filename, sql_filename

if __name__ == "__main__":
    export_data()
