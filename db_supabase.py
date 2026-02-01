from supabase import create_client, Client
import uuid
import config

# Konfigurasi Supabase
SUPABASE_URL = config.SUPABASE_URL
SUPABASE_KEY = config.SUPABASE_KEY

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error initializing Supabase: {e}")
    supabase = None

def get_mitras():
    """Mengambil data mitra dari Supabase untuk ditampilkan di Katalog"""
    if not supabase: return []
    try:
        response = supabase.table('partners').select("*").execute()
        raw_data = response.data
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "db_id": item.get('id'),
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
                "db_id": item.get('id'),
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
        raw_data = response.data
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "db_id": item.get('id'),
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
        raw_data = response.data
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "db_id": item.get('id'),
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
    """Menyimpan klaim voucher ke Supabase dengan validasi 1 kali klaim per mitra"""
    if not supabase: return "db_error"
    try:
        # 1. Cek apakah user sudah pernah klaim di mitra ini
        existing_claim = supabase.table('voucher_claims').select("id").eq('user_id', str(user_id)).eq('mitra', mitra).execute()
        
        if existing_claim.data and len(existing_claim.data) > 0:
            return "already_claimed"

        # 2. Jika belum, simpan data baru
        data = {
            "user_id": str(user_id),
            "user_name": user_name,
            "mitra": mitra,
            "promo": promo,
            "resi": resi
            # "timestamp": "now()" -- Biarkan default DB yang mengisi
        }
        supabase.table('voucher_claims').insert(data).execute()
        return "success"
    except Exception as e:
        print(f"Error saving claim: {e}")
        return f"error: {str(e)}"

def get_all_claims():
    """Mengambil semua data klaim voucher untuk laporan PDF"""
    if not supabase: return []
    try:
        response = supabase.table('voucher_claims').select("*").order('timestamp', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching claims: {e}")
        return []

# --- CRUD Operations for Dashboard ---

def create_record(table, data):
    """Generic create function"""
    if not supabase: return None
    try:
        response = supabase.table(table).insert(data).execute()
        return response.data
    except Exception as e:
        print(f"Error creating record in {table}: {e}")
        return None

def update_record(table, id, data):
    """Generic update function"""
    if not supabase: return None
    try:
        response = supabase.table(table).update(data).eq('id', id).execute()
        return response.data
    except Exception as e:
        print(f"Error updating record in {table} id {id}: {e}")
        return None

def delete_record(table, id):
    """Generic delete function"""
    if not supabase: return False
    try:
        supabase.table(table).delete().eq('id', id).execute()
        return True
    except Exception as e:
        print(f"Error deleting record in {table} id {id}: {e}")
        return False

def upload_image(file_bytes, filename, content_type):
    """Upload image to Supabase Storage and return Public URL"""
    if not supabase: return None
    try:
        bucket = 'images'
        path = f"uploads/{filename}"
        
        # Upload
        supabase.storage.from_(bucket).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        
        # Get Public URL
        public_url = supabase.storage.from_(bucket).get_public_url(path)
        return public_url
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None
