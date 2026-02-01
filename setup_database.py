import sqlite3
import os

def init_db():
    if not os.path.exists('database'): os.makedirs('database')
    conn = sqlite3.connect('database/mercure.db')
    cursor = conn.cursor()

    # Tabel Partners [cite: 114]
    cursor.execute('DROP TABLE IF EXISTS partners')
    cursor.execute('''CREATE TABLE partners (
        id INTEGER PRIMARY KEY, name TEXT, category TEXT, 
        latitude REAL, longitude REAL, promo_detail TEXT)''')

    # Tabel Sessions (Aktivasi Tamu) [cite: 106]
    cursor.execute('''CREATE TABLE IF NOT EXISTS hotel_sessions (
        telegram_user_id INTEGER PRIMARY KEY, 
        activated_at TIMESTAMP, expired_at TIMESTAMP, status TEXT)''')

    # Tabel Vouchers (Cegah Duplikat) [cite: 119]
    cursor.execute('''CREATE TABLE IF NOT EXISTS vouchers (
        voucher_code TEXT PRIMARY KEY, telegram_user_id INTEGER, 
        partner_id INTEGER, created_at TIMESTAMP)''')

    # Isi Data Mitra [cite: 140-144, 202]
    partners = [
        (1, 'Kedai Lucky', 'Cafe', -6.904924, 107.629197, 'Diskon 10%'),
        (2, 'Mie Gacoan', 'Resto', -6.899612, 107.628515, 'Diskon 10%'),
        (3, 'Sate Jando', 'Street Food', -6.901525, 107.618644, 'Diskon 10%'),
        (4, 'Iga Si Jangkung', 'Resto', -6.892543, 107.604523, 'Diskon 10%'),
        (5, 'Kingsley', 'Snack', -6.917452, 107.615231, 'Diskon 10%'),
        (6, 'Sudarasa', 'Coffee', -6.903821, 107.632145, 'Diskon 10%'),
        (7, 'Bebek Ali', 'Resto', -6.892112, 107.616334, 'Diskon 10%'),
        (8, 'Warung Bu Imas', 'Sunda', -6.924812, 107.605312, 'Diskon 10%'),
        (9, 'Ambrogio', 'Bakery', -6.913521, 107.622415, 'Diskon 10%'),
        (10, 'Nasgor AA', 'Resto', -6.890123, 107.615432, 'Diskon 10%')
    ]
    cursor.executemany('INSERT INTO partners VALUES (?,?,?,?,?,?)', partners)
    conn.commit()
    conn.close()
    print("✅ Database Lucky Berhasil Diupdate sesuai Spesifikasi!")

if __name__ == '__main__': init_db()