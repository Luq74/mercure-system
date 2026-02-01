import json
import os
import sys
from supabase import create_client
import config

# Inisialisasi Client Supabase dengan konfigurasi dari config.py
try:
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
except Exception as e:
    print(f"Error koneksi Supabase: {e}")
    sys.exit(1)

# Daftar tabel yang akan di-backup/restore
TABLES = ['partners', 'attractions', 'hotel_promos', 'events', 'voucher_claims']
BACKUP_DIR = 'backup_data'

def backup():
    """Mengunduh semua data dari Supabase ke file JSON lokal"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    print(f"🚀 Memulai BACKUP dari {config.SUPABASE_URL}...")
    
    for table in TABLES:
        print(f"📥 Mengambil data tabel '{table}'...", end=" ")
        try:
            response = supabase.table(table).select("*").execute()
            data = response.data
            
            filepath = os.path.join(BACKUP_DIR, f"{table}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ OK ({len(data)} baris)")
        except Exception as e:
            print(f"❌ Gagal: {e}")
            
    print(f"\n✨ Backup Selesai! Data tersimpan di folder '{BACKUP_DIR}'")
    print("⚠️  Sekarang aman untuk menghapus Project lama di Dashboard Supabase.")

def restore():
    """Mengupload data dari file JSON lokal ke Supabase baru"""
    if not os.path.exists(BACKUP_DIR):
        print(f"❌ Folder '{BACKUP_DIR}' tidak ditemukan. Jalankan backup dulu!")
        return

    print(f"🚀 Memulai RESTORE ke {config.SUPABASE_URL}...")
    print("⚠️  Pastikan Anda sudah menjalankan script SQL 'setup_supabase.sql' di project baru!")
    
    for table in TABLES:
        filepath = os.path.join(BACKUP_DIR, f"{table}.json")
        if not os.path.exists(filepath):
            print(f"⚠️  File backup untuk '{table}' tidak ditemukan, dilewati.")
            continue
            
        print(f"📤 Mengupload data ke tabel '{table}'...", end=" ")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                print("⚠️  Data kosong, dilewati.")
                continue
                
            # Insert data (Supabase akan handle ID jika diset Identity BY DEFAULT)
            # Jika ada error duplicate key, kita ignore atau handle?
            # Untuk migrasi bersih (tabel kosong), insert langsung aman.
            supabase.table(table).insert(data).execute()
            print(f"✅ OK ({len(data)} baris)")
            
        except Exception as e:
            print(f"❌ Gagal: {e}")
            print("   (Mungkin data sudah ada? Coba kosongkan tabel dulu jika perlu)")

    print("\n✨ Restore Selesai! Sistem siap digunakan di Project baru.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        restore()
    else:
        print("ℹ️  Mode: BACKUP (Default)")
        print("   Untuk restore, jalankan: python backup_restore.py restore")
        print("   -----------------------------------------------------")
        backup()
