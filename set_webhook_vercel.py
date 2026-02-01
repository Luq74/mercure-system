import urllib.request
import urllib.parse
import json
import config

TOKEN = config.BOT_TOKEN
VERCEL_URL = config.VERCEL_URL

# Hapus trailing slash jika ada
if VERCEL_URL.endswith('/'):
    VERCEL_URL = VERCEL_URL[:-1]

WEBHOOK_URL = f"{VERCEL_URL}/webhook"
API_URL = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"

print(f"Mengatur Webhook ke: {WEBHOOK_URL}")
print("-" * 50)

try:
    with urllib.request.urlopen(API_URL) as response:
        result = json.loads(response.read().decode())
        if result.get('ok'):
            print("✅ SUKSES! Webhook berhasil diatur.")
            print(f"Telegram sekarang akan mengirim pesan ke: {WEBHOOK_URL}")
            print("Silakan coba ketik /start lagi di bot Anda.")
        else:
            print("❌ GAGAL!")
            print(f"Pesan error: {result.get('description')}")
except Exception as e:
    print("❌ ERROR TERJADI:")
    print(e)
    print("\nPastikan koneksi internet lancar.")
