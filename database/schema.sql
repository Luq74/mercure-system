-- Tabel User dan Sesi [cite: 102, 106]
CREATE TABLE IF NOT EXISTS users (
    telegram_user_id BIGINT PRIMARY KEY,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hotel_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id BIGINT,
    status TEXT DEFAULT 'ACTIVE',
    expired_at TIMESTAMP
);

-- Tabel Mitra & Voucher [cite: 114, 119]
CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE IF NOT EXISTS vouchers (
    voucher_code TEXT PRIMARY KEY,
    telegram_user_id BIGINT,
    partner_id INTEGER,
    status TEXT DEFAULT 'GENERATED' -- GENERATED/USED [cite: 125]
);

-- Masukkan data mitra awal [cite: 140-144]
INSERT OR IGNORE INTO partners (name, latitude, longitude) VALUES ('Kedai Lucky', -6.902462, 107.635841);
INSERT OR IGNORE INTO partners (name, latitude, longitude) VALUES ('Mie Gacoan', -6.9030, 107.6360);