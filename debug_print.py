import sys
print("Test output 1", flush=True)
sys.stdout.write("Test output 2\n")
sys.stdout.flush()
try:
    import supabase
    print("Supabase module found", flush=True)
except ImportError as e:
    print(f"Supabase module missing: {e}", flush=True)

import config
print(f"URL: {config.SUPABASE_URL}", flush=True)
