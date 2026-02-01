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
        # Asumsi struktur sama dengan wisata
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

def upload_image(file_bytes, file_name, content_type):
    """Upload image to Supabase Storage"""
    if not supabase: return None
    try:
        bucket_name = "images"
        # Upload file
        response = supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        
        # Get Public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        return public_url
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def upload_image(file_bytes, file_name, content_type):
    """Upload image to Supabase Storage"""
    if not supabase: return None
    try:
        # Generate unique filename
        unique_name = f"{uuid.uuid4()}-{file_name}"
        bucket_name = "images"
        
        # Upload
        supabase.storage.from_(bucket_name).upload(
            path=unique_name,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        
        # Get Public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(unique_name)
        return public_url
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def upload_image(file_bytes, filename, content_type):
    """Upload image to Supabase Storage and return Public URL"""
    if not supabase: return None
    try:
        bucket = 'images'
        # Check if bucket exists? No easy way with py-client anon key usually. 
        # Assume 'images' bucket exists and is public.
        
        # Upload
        path = f"uploads/{filename}"
        res = supabase.storage.from_(bucket).upload(
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
