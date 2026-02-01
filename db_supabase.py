from supabase import create_client, Client

# Konfigurasi Supabase
# NOTE: Idealnya ini ada di environment variables, tapi untuk kemudahan deployment awal kita taruh sini
SUPABASE_URL = "https://wvizrrovgtpbohenruuz.supabase.co"
SUPABASE_KEY = "sb_publishable_fswaWOXcENr45Ce-R6tkEQ_TreMgKue" 

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error initializing Supabase: {e}")
    supabase = None

def get_mitras():
    """Mengambil data mitra dari Supabase untuk ditampilkan di Katalog"""
    if not supabase: return []
    try:
        # Mengambil semua kolom dari tabel 'partners'
        response = supabase.table('partners').select("*").execute()
        raw_data = response.data
        
        # Transform data agar sesuai format JS di frontend
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "img": item.get('image_url', ''),
                "id": { "name": item.get('name_id', item.get('name', '')), "desc": item.get('desc_id', '') },
                "en": { "name": item.get('name_en', item.get('name', '')), "desc": item.get('desc_en', '') },
                "cn": { "name": item.get('name_cn', item.get('name', '')), "desc": item.get('desc_cn', '') }
            })
        return formatted_data
    except Exception as e:
        print(f"Error fetching mitras: {e}")
        return []

def get_wisata():
    """Mengambil data wisata dari Supabase"""
    if not supabase: return []
    try:
        response = supabase.table('attractions').select("*").execute()
        raw_data = response.data
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "img": item.get('image_url', ''),
                "url": item.get('map_url', ''),
                "id": { "title": item.get('title_id', ''), "desc": item.get('desc_id', '') },
                "en": { "title": item.get('title_en', ''), "desc": item.get('desc_en', '') },
                "cn": { "title": item.get('title_cn', ''), "desc": item.get('desc_cn', '') }
            })
        return formatted_data
    except Exception as e:
        print(f"Error fetching wisata: {e}")
        return []

def get_promos():
    """Mengambil data promo hotel"""
    if not supabase: return []
    try:
        response = supabase.table('hotel_promos').select("*").execute()
        # Asumsi struktur sama dengan wisata (title/desc + img)
        raw_data = response.data
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "img": item.get('image_url', ''),
                "id": { "title": item.get('title_id', ''), "desc": item.get('desc_id', '') },
                "en": { "title": item.get('title_en', ''), "desc": item.get('desc_en', '') },
                "cn": { "title": item.get('title_cn', ''), "desc": item.get('desc_cn', '') }
            })
        return formatted_data
    except Exception as e:
        print(f"Error fetching promos: {e}")
        return []

def get_events():
    """Mengambil data event"""
    if not supabase: return []
    try:
        response = supabase.table('events').select("*").execute()
        # Asumsi struktur sama dengan wisata
        raw_data = response.data
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "img": item.get('image_url', ''),
                "id": { "title": item.get('title_id', ''), "desc": item.get('desc_id', '') },
                "en": { "title": item.get('title_en', ''), "desc": item.get('desc_en', '') },
                "cn": { "title": item.get('title_cn', ''), "desc": item.get('desc_cn', '') }
            })
        return formatted_data
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def save_claim(user_id, user_name, mitra, promo, resi):
    """Menyimpan klaim voucher ke Supabase"""
    if not supabase: return False
    try:
        data = {
            "user_id": str(user_id),
            "user_name": user_name,
            "mitra": mitra,
            "promo": promo,
            "resi": resi,
            "timestamp": "now()"
        }
        supabase.table('voucher_claims').insert(data).execute()
        return True
    except Exception as e:
        print(f"Error saving claim: {e}")
        return False
