#!/usr/bin/env python
"""
Script to import data into Railway PostgreSQL database
Run this after setting up Railway database
"""
import os
import django
import json
from datetime import datetime

def import_data(export_file):
    """Import data from export file into Railway database"""
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
    django.setup()
    
    from django.core import serializers
    from django.db import transaction
    from realestate.models import Agent, Customer, Payment, Project, Gift, AgentGift
    
    print("🔄 Starting data import to Railway...")
    
    # Load export data
    with open(export_file, 'r') as f:
        export_data = json.load(f)
    
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
                    # Clear existing data for this model (except gifts and projects)
                    if model_name not in ['gifts', 'projects']:
                        model_class.objects.all().delete()
                        print(f"🗑️  Cleared existing {model_name}")
                    
                    # Deserialize and save objects
                    serialized_data = json.dumps(export_data[model_name])
                    objects = serializers.deserialize('json', serialized_data)
                    
                    count = 0
                    for obj in objects:
                        obj.save()
                        count += 1
                    
                    print(f"✅ Imported {count} {model_name}")
                    
                except Exception as e:
                    print(f"❌ Error importing {model_name}: {e}")
                    # Continue with other models
    
    print("🎉 Data import completed successfully!")
    print("🔍 Verifying import...")
    
    # Verify import
    print(f"Agents: {Agent.objects.count()}")
    print(f"Customers: {Customer.objects.count()}")
    print(f"Projects: {Project.objects.count()}")
    print(f"Payments: {Payment.objects.count()}")
    print(f"Gifts: {Gift.objects.count()}")
    print(f"Agent Gifts: {AgentGift.objects.count()}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python import_railway_data.py <export_file.json>")
        sys.exit(1)
    
    export_file = sys.argv[1]
    import_data(export_file)
