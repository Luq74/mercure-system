import db_supabase
import json

print("Testing db_supabase...")

try:
    print("\n--- Testing get_mitras ---")
    mitras = db_supabase.get_mitras()
    print(f"Mitras count: {len(mitras)}")
    if mitras:
        print("First mitra sample:", json.dumps(mitras[0], indent=2))

    print("\n--- Testing get_wisata ---")
    wisata = db_supabase.get_wisata()
    print(f"Wisata count: {len(wisata)}")
    if wisata:
        print("First wisata sample:", json.dumps(wisata[0], indent=2))
        
    print("\n--- Testing get_promos ---")
    promos = db_supabase.get_promos()
    print(f"Promos count: {len(promos)}")
    if promos:
        print("First promo sample:", json.dumps(promos[0], indent=2))
        
    print("\n--- Testing get_events ---")
    events = db_supabase.get_events()
    print(f"Events count: {len(events)}")
    if events:
        print("First event sample:", json.dumps(events[0], indent=2))
        
    print("\n--- Testing get_all_claims ---")
    claims = db_supabase.get_all_claims()
    print(f"Claims count: {len(claims)}")
    if claims:
        print("First claim sample:", json.dumps(claims[0], indent=2))

except Exception as e:
    print(f"Error during testing: {e}")
