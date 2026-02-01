from supabase import create_client
import config
import sys

# Redirect stdout to file
sys.stdout = open('db_check_result.txt', 'w', encoding='utf-8')

print("Checking database connection...")
try:
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    # 1. Check voucher_claims table
    print("Checking 'voucher_claims' table...")
    try:
        response = supabase.table('voucher_claims').select("*").limit(1).execute()
        print("✅ Table 'voucher_claims' EXISTS.")
        print(f"   Data sample: {response.data}")
    except Exception as e:
        print(f"❌ Table 'voucher_claims' ERROR: {e}")
        
    # 2. Check partners table
    print("\nChecking 'partners' table...")
    try:
        response = supabase.table('partners').select("*").limit(1).execute()
        print("✅ Table 'partners' EXISTS.")
    except Exception as e:
        print(f"❌ Table 'partners' ERROR: {e}")

except Exception as e:
    print(f"❌ Connection ERROR: {e}")

sys.stdout.close()
