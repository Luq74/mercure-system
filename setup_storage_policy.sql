-- Enable RLS for storage (usually enabled by default)
alter table storage.objects enable row level security;

-- 1. Pastikan bucket 'images' ada dan diset sebagai PUBLIC
insert into storage.buckets (id, name, public)
values ('images', 'images', true)
on conflict (id) do update set public = true;

-- 2. Hapus policy lama jika ada (untuk menghindari konflik)
drop policy if exists "Public Access" on storage.objects;
drop policy if exists "Allow Public Select" on storage.objects;
drop policy if exists "Allow Public Insert" on storage.objects;
drop policy if exists "Allow Public Update" on storage.objects;
drop policy if exists "Allow Public Delete" on storage.objects;

-- 3. Buat SATU Policy Super Longgar untuk bucket 'images'
-- Ini mengizinkan SELECT, INSERT, UPDATE, DELETE untuk SEMUA orang (Anonim & Login)
create policy "Public Access"
on storage.objects for all
using ( bucket_id = 'images' )
with check ( bucket_id = 'images' );

-- Catatan:
-- Script ini membuat bucket 'images' menjadi sepenuhnya publik dan bisa diakses/ditulis oleh siapa saja.
-- Sangat cocok untuk memudahkan pengembangan fitur upload staff.
