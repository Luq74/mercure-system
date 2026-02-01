# core/voucher.py
import secrets
import string

def generate_voucher_code():
    chars = string.ascii_uppercase + string.digits
    return "NEXA-" + "".join(secrets.choice(chars) for _ in range(8))

def get_voucher_text(partner_name, code):
    return (
        f"🎟️ VOUCHER DISKON 10% 🎟️\n"
        f"--------------------------\n"
        f"Mitra: {partner_name}\n"
        f"Kode: {code}\n"
        f"Status: Valid (Sekali Pakai)\n"
        f"--------------------------\n"
        f"Tunjukkan pesan ini ke kasir {partner_name}."
    )