import json
import os
import sys
import config
from supabase import create_client, Client

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')

print("=== STARTING RESTORE SCRIPT ===")

# Initialize Supabase
try:
    print(f"Connecting to: {config.SUPABASE_URL}", flush=True)
    supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    print("Connection initialized.", flush=True)
except Exception as e:
    print(f"Error initializing Supabase: {e}", flush=True)
    exit(1)

BACKUP_FILE = 'backup_mercure_data.json'

def restore_data():
    if not os.path.exists(BACKUP_FILE):
        print(f"❌ Backup file not found: {BACKUP_FILE}", flush=True)
        return

    print(f"Reading backup file...", flush=True)
    
    try:
        with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}", flush=True)
        return

    for table, records in all_data.items():
        print(f"Restoring table: {table} ({len(records)} records)...", end=" ", flush=True)
        
        if not records:
            print("Skipping (No data)", flush=True)
            continue

        success_count = 0
        fail_count = 0

        for record in records:
             try:
                 # Gunakan upsert agar jika data sudah ada, di-update
                 supabase.table(table).upsert(record).execute()
                 success_count += 1
             except Exception as insert_e:
                 # Ignore duplicate key error quietly, print others
                 if "duplicate key value" not in str(insert_e):
                    print(f"\n   Error inserting row {record.get('id')}: {insert_e}", flush=True)
                 fail_count += 1
        
        print(f"Done (Success: {success_count}, Failed/Skip: {fail_count})", flush=True)

    print(f"\n✅ Restore complete!", flush=True)

if __name__ == "__main__":
    restore_data()
