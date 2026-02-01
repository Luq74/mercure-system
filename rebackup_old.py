
import json
import os
import sys
from supabase import create_client, Client

# Kredensial LAMA (Hardcoded dari key Mercure System.txt)
OLD_URL = "https://wvizrrovgtpbohenruuz.supabase.co"
# Ambil string key saja, buang spasi/teks "Secret keys"
OLD_KEY = "sb_secret_dJAJ_6YprqWs2lkyHGDTZw_Vc06mwjl" 

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')

print("=== STARTING EMERGENCY RE-BACKUP ===")
print(f"Target URL: {OLD_URL}")

# Initialize Supabase
try:
    supabase: Client = create_client(OLD_URL, OLD_KEY)
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
        
        print(f"\n✅ Re-Backup complete! Data saved to: {os.path.abspath(BACKUP_FILE)}")
    except Exception as e:
        print(f"\n❌ Error saving file: {e}")

if __name__ == "__main__":
    backup_data()
