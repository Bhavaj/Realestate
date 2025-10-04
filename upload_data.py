#!/usr/bin/env python
"""
Script to upload data to Railway using Railway CLI
"""
import subprocess
import os

def upload_data_file():
    """Upload the data export file to Railway"""
    
    export_file = "data_export/render_data_export_20251003_192946.json"
    
    if not os.path.exists(export_file):
        print(f"❌ Export file not found: {export_file}")
        return False
    
    print(f"📤 Uploading {export_file} to Railway...")
    
    try:
        # Use Railway CLI to upload the file
        result = subprocess.run([
            "railway", "run", "--service", "web", 
            "python", "import_railway_data.py", export_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Data uploaded successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Upload failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error uploading data: {e}")
        return False

if __name__ == "__main__":
    upload_data_file()
