import json
import os
import sys
import config
from supabase import create_client, Client

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')

print("=== STARTING BACKUP SCRIPT ===")
print("Checking imports...", flush=True)

# Initialize Supabase
try:
    print(f"Connecting to: {config.SUPABASE_URL}", flush=True)
    supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    print("Connection initialized.", flush=True)
except Exception as e:
    print(f"Error initializing Supabase: {e}", flush=True)
    exit(1)

TABLES = ['partners', 'attractions', 'hotel_promos', 'events', 'voucher_claims']
BACKUP_FILE = 'backup_mercure_data.json'

def backup_data():
    print(f"Starting backup process...", flush=True)
    all_data = {}
    
    for table in TABLES:
        print(f"Backing up table: {table}...", end=" ", flush=True)
        try:
            # Select all columns
            response = supabase.table(table).select("*").execute()
            data = response.data
            all_data[table] = data
            print(f"Done ({len(data)} records)", flush=True)
        except Exception as e:
            print(f"FAILED: {e}", flush=True)
            all_data[table] = []

    # Save to file
    try:
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Backup complete! Data saved to: {os.path.abspath(BACKUP_FILE)}")
        print("Simpan file ini baik-baik sebelum menghapus project Supabase lama.")
    except Exception as e:
        print(f"\n❌ Error saving file: {e}")

if __name__ == "__main__":
    backup_data()
