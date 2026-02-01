import db_supabase
from supabase import create_client, Client

# Konfigurasi Supabase (from db_supabase.py)
SUPABASE_URL = "https://wvizrrovgtpbohenruuz.supabase.co"
SUPABASE_KEY = "sb_publishable_fswaWOXcENr45Ce-R6tkEQ_TreMgKue" 

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client initialized.")
    
    print("\n--- Testing Storage Access ---")
    try:
        buckets = supabase.storage.list_buckets()
        print(f"Buckets found: {len(buckets)}")
        for b in buckets:
            print(f"- {b.name}")
            
        # Try to verify 'images' bucket specifically
        images_bucket = next((b for b in buckets if b.name == 'images'), None)
        if images_bucket:
            print("Bucket 'images' exists.")
        else:
            print("Bucket 'images' DOES NOT exist. Uploads will fail.")
            
    except Exception as e:
        print(f"Error listing buckets (likely permission issue with anon key): {e}")
        # Anon key usually cannot list buckets. But it can upload if policy allows.
        
except Exception as e:
    print(f"Error: {e}")
