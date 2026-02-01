import threading, datetime, random, logging, sqlite3, os, io, asyncio
from flask import Flask, render_template, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from languages import TRANSLATIONS
import db_supabase
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# KONFIGURASI UTAMA
# NOTE: Di Vercel, URL_BASE ini harus diganti dengan URL Vercel Anda (misal: https://mercure-bot.vercel.app)
URL_BASE = "https://mercure-system.vercel.app"
TOKEN = "8270937316:AAEEb1GUN_xeng84808iGBsMJrnBDwi_tpg"
ID_STAFF = "784633296"  # ID Telegram Staff yang diizinkan

# Database Setup (Legacy SQLite for local testing or backup, but we use Supabase now)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "mercure.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS voucher_claims
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_name TEXT,
                  user_id TEXT,
                  mitra TEXT,
                  promo TEXT,
                  resi TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

# Initialize DB (Warning: On Vercel, this is read-only/ephemeral)
try:
    init_db()
except Exception as e:
    logging.warning(f"Database init failed (normal on Vercel if read-only): {e}")

# In-memory storage for user language preference
user_languages = {}

# Flags
FLAGS = {
    'id': "🇮🇩",
    'en': "🇬🇧",
    'cn': "🇨🇳"
}

app = Flask(__name__)

# Error Handler untuk Debugging di Vercel
@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e,  Exception):
        logging.error(f"Server Error: {e}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500
    return f"Unknown Error", 500

def get_text(lang_code, key, **kwargs):
    return TRANSLATIONS.get(lang_code, TRANSLATIONS['id']).get(key, key).format(**kwargs)

@app.route('/')
def index(): 
    lang = request.args.get('lang', 'id')
    mitras = db_supabase.get_mitras()
    return render_template('index.html', lang=lang, mitras=mitras)

@app.route('/wisata')
def wisata(): 
    lang = request.args.get('lang', 'id')
    wisata_list = db_supabase.get_wisata()
    return render_template('wisata.html', lang=lang, wisata_list=wisata_list)

@app.route('/promo')
def promo(): 
    lang = request.args.get('lang', 'id')
    promos = db_supabase.get_promos()
    return render_template('promo.html', lang=lang, promos=promos)

@app.route('/event')
def event(): 
    lang = request.args.get('lang', 'id')
    events = db_supabase.get_events()
    return render_template('event.html', lang=lang, events=events)

# --- DASHBOARD ROUTES ---

@app.route('/dashboard')
def dashboard():
    """Halaman Dashboard Admin"""
    mitras = db_supabase.get_mitras()
    wisata = db_supabase.get_wisata()
    promos = db_supabase.get_promos()
    events = db_supabase.get_events()
    return render_template('dashboard.html', mitras=mitras, wisata=wisata, promos=promos, events=events)

@app.route('/api/create/<table_name>', methods=['POST'])
def api_create(table_name):
    """API untuk Create Record dengan Upload Gambar"""
    try:
        data = request.form.to_dict()
        
        # Handle File Upload
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename != '':
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}_{file.filename}"
                file_bytes = file.read()
                public_url = db_supabase.upload_image(file_bytes, filename, file.content_type)
                if public_url:
                    data['image_url'] = public_url
        
        # Clean up empty fields if any (optional)
        
        result = db_supabase.create_record(table_name, data)
        if result:
            return jsonify({"status": "success", "data": result}), 200
        return jsonify({"status": "error", "message": "Failed to create record"}), 500
    except Exception as e:
        logging.error(f"API Create Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/update/<table_name>/<id>', methods=['POST'])
def api_update(table_name, id):
    """API untuk Update Record dengan Upload Gambar"""
    try:
        data = request.form.to_dict()
        
        # Handle File Upload
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename != '':
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}_{file.filename}"
                file_bytes = file.read()
                public_url = db_supabase.upload_image(file_bytes, filename, file.content_type)
                if public_url:
                    data['image_url'] = public_url
        
        # Jika user tidak upload gambar baru, jangan update field image_url (frontend harus handle ini, 
        # tapi di sini kita terima form data. Jika image_url tidak dikirim, jangan dihapus dari DB?)
        # Supabase update hanya field yang dikirim. Jadi aman.
        # Tapi hati-hati, request.form.to_dict() akan mengambil semua input hidden.
        # Pastikan di frontend input hidden image_url diisi URL lama, atau dihapus jika upload baru.
        
        result = db_supabase.update_record(table_name, id, data)
        if result:
            return jsonify({"status": "success", "data": result}), 200
        return jsonify({"status": "error", "message": "Failed to update record"}), 500
    except Exception as e:
        logging.error(f"API Update Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/delete/<table_name>/<id>', methods=['POST', 'DELETE'])
def api_delete(table_name, id):
    """API untuk Delete Record"""
    result = db_supabase.delete_record(table_name, id)
    if result:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API untuk Upload Image"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file:
        # Generate unique filename to avoid collision
        import uuid
        ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        
        # Read file content
        file_content = file.read()
        
        # Upload to Supabase
        public_url = db_supabase.upload_image(file_content, filename, file.content_type)
        
        if public_url:
            return jsonify({"status": "success", "url": public_url}), 200
        else:
            return jsonify({"status": "error", "message": "Upload failed"}), 500

# --- END DASHBOARD ROUTES ---

def get_main_keyboard(lang_code):
    t = lambda key: get_text(lang_code, key)
    kb = [
        [KeyboardButton(t('btn_catalog'), web_app=WebAppInfo(url=f"{URL_BASE}/?lang={lang_code}"))],
        [KeyboardButton(t('btn_wisata'), web_app=WebAppInfo(url=f"{URL_BASE}/wisata?lang={lang_code}")), 
         KeyboardButton(t('btn_promo'), web_app=WebAppInfo(url=f"{URL_BASE}/promo?lang={lang_code}"))],
        [KeyboardButton(t('btn_event'), web_app=WebAppInfo(url=f"{URL_BASE}/event?lang={lang_code}"))],
        [KeyboardButton(t('btn_shalat')), KeyboardButton(t('btn_lost_found'))],
        [KeyboardButton(t('btn_emergency')), KeyboardButton(FLAGS['id']), KeyboardButton(FLAGS['en']), KeyboardButton(FLAGS['cn'])]
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def generate_pdf_report(buffer):
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(name='HeaderStandard', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=10)
    elements.append(Paragraph("Mercure Hotels Bandung Nexa Supratman", header_style))
    elements.append(Paragraph("Laporan Klaim Voucher Mitra", header_style))
    elements.append(Spacer(1, 0.2*inch))

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT user_name, resi, timestamp, mitra, promo FROM voucher_claims ORDER BY id DESC")
        data = c.fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Database error in PDF generation: {e}")
        elements.append(Paragraph(f"Error mengambil data database: {e}", styles['Normal']))
        doc.build(elements)
        return

    if not data:
        elements.append(Paragraph("Belum ada data klaim voucher.", styles['Normal']))
    else:
        table_data = [['Nama Tamu', 'No. Resi', 'Waktu', 'Mitra', 'Promo']]
        for row in data:
            table_data.append([row[0], row[1], row[2], row[3], row[4]])

        col_widths = [1.0*inch, 1.3*inch, 1.3*inch, 1.5*inch, 1.2*inch] 
        
        t = Table(table_data, colWidths=col_widths, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5D2F61')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t)

    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(name='Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
    elements.append(Paragraph("Laporan Dibuat oleh Sentra Guest OS V1.5", footer_style))

    doc.build(elements)

async def ctk_lap_mitra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != ID_STAFF:
        await update.message.reply_text("⛔ Akses ditolak. Perintah ini hanya untuk Staff Hotel.")
        return

    buffer = io.BytesIO()
    try:
        logging.info("DEBUG: Starting PDF generation...")
        generate_pdf_report(buffer)
        buffer.seek(0)
        await update.message.reply_document(
            document=buffer,
            filename="laporan_mitra_v7.pdf", 
            caption="📄 **Laporan Klaim Voucher Mitra**",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Error generating PDF: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Gagal membuat laporan: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_languages:
        user_languages[user_id] = 'id'
    
    lang_code = user_languages[user_id]
    welcome = get_text(lang_code, 'welcome')
    await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=get_main_keyboard(lang_code))

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.effective_message.web_app_data.data.split('|')
    mitra, resi, promo = data[0], data[1], data[2]
    
    webapp_lang = 'id'
    if len(data) > 3:
        webapp_lang = data[3]
        
    user, waktu = update.effective_user, datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    
    # Simpan ke Supabase
    try:
        success = db_supabase.save_claim(user.id, user.first_name, mitra, promo, resi)
        if not success:
            logging.error("Gagal menyimpan ke Supabase")
    except Exception as e:
        logging.error(f"Gagal menyimpan data voucher: {e}")

    user_languages[user.id] = webapp_lang
    lang_code = webapp_lang

    laporan_staff = (
        f"🚨 **LAPORAN KLAIM VOUCHER BARU**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 **No. Resi:** `{resi}`\n"
        f"📅 **Waktu:** {waktu}\n\n"
        f"👤 **Nama Tamu:** {user.first_name}\n"
        f"🆔 **ID Telegram:** `{user.id}`\n\n"
        f"🎫 **Mitra:** {mitra}\n"
        f"🎁 **Promo:** {promo}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    await context.bot.send_message(chat_id=ID_STAFF, text=laporan_staff, parse_mode='Markdown',
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"Chat {user.first_name}", url=f"tg://user?id={user.id}")]]))
    
    msg_success = get_text(lang_code, 'msg_voucher_success', mitra=mitra, promo=promo, resi=resi)
    await update.message.reply_text(msg_success, parse_mode='Markdown')

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, user = update.message.text, update.effective_user
    user_id = user.id
    
    if text == FLAGS['id']:
        user_languages[user_id] = 'id'
        await update.message.reply_text(get_text('id', 'lang_selected'), reply_markup=get_main_keyboard('id'))
        return
    elif text == FLAGS['en']:
        user_languages[user_id] = 'en'
        await update.message.reply_text(get_text('en', 'lang_selected'), reply_markup=get_main_keyboard('en'))
        return
    elif text == FLAGS['cn']:
        user_languages[user_id] = 'cn'
        await update.message.reply_text(get_text('cn', 'lang_selected'), reply_markup=get_main_keyboard('cn'))
        return

    lang_code = user_languages.get(user_id, 'id')
    t = lambda key, **kwargs: get_text(lang_code, key, **kwargs)
    
    if text == t('btn_emergency'):
        await context.bot.send_message(chat_id=ID_STAFF, 
                                       text=t('msg_emergency', name=user.first_name, id=user.id), 
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"Hubungi Tamu", url=f"tg://user?id={user.id}")]]))
        await update.message.reply_text(t('msg_emergency_reply'))
        
    elif text == t('btn_lost_found'):
        await context.bot.send_message(chat_id=ID_STAFF, 
                                       text=t('msg_lost_found', name=user.first_name, id=user.id), 
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"Chat Tamu", url=f"tg://user?id={user.id}")]]))
        await update.message.reply_text(t('msg_lost_found_reply'))
        
    elif text == t('btn_shalat'):
        await update.message.reply_text(t('msg_shalat'))
        
    else:
        laporan = (f"📩 **DETAIL PESAN TAMU**\n━━━━━━━━━━━━━━━━━━━━\n"
                   f"👤 **Dari:** {user.first_name}\n"
                   f"🆔 **ID:** `{user.id}`\n"
                   f"💬 **Isi Pesan:** {text}")
        await context.bot.send_message(chat_id=ID_STAFF, text=laporan, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Balas Pesan", url=f"tg://user?id={user.id}")]]))
        await update.message.reply_text(t('msg_default_reply'))

async def post_init(application: Application):
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Mulai Bot / Reset"),
            BotCommand("ctk_lap_mitra", "Cetak Laporan Mitra (PDF)")
        ],
        scope=BotCommandScopeChat(chat_id=ID_STAFF)
    )

# GLOBAL BOT APP (For Vercel)
# NOTE: Di environment serverless seperti Vercel, kita tidak bisa menggunakan global app 
# yang persisten karena event loop akan di-reset setiap request.
# Jadi kita buat factory function.

def create_app():
    return Application.builder().token(TOKEN).post_init(post_init).build()

# Handler Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint untuk Vercel Webhook"""
    if request.method == "POST":
        # Decode update tanpa bot dulu (karena bot ada di dalam async process)
        # Atau gunakan temporary bot untuk decoding jika perlu, tapi de_json biasanya butuh bot untuk shortcut
        # Kita buat app dulu
        
        # Gunakan new_event_loop untuk setiap request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Buat app baru yang terikat dengan loop ini
            ptb_app = create_app()
            
            # Tambahkan handler (harus di-add setiap kali buat app baru)
            ptb_app.add_handler(CommandHandler("start", start))
            ptb_app.add_handler(CommandHandler("ctk_lap_mitra", ctk_lap_mitra))
            ptb_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
            ptb_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_all_messages))
            
            # Decode update
            update = Update.de_json(request.get_json(force=True), ptb_app.bot)
            
            async def process():
                await ptb_app.initialize()
                await ptb_app.process_update(update)
                await ptb_app.shutdown()
            
            loop.run_until_complete(process())
        finally:
            loop.close()
            
        return "OK"
    return "Invalid Request"

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Helper untuk set webhook (panggil ini setelah deploy ke Vercel)"""
    url = request.args.get('url')
    if url:
        # Hapus trailing slash
        if url.endswith('/'): url = url[:-1]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ptb_app = create_app()
            async def set_hook():
                await ptb_app.bot.set_webhook(url + "/webhook")
                await ptb_app.shutdown()
            
            loop.run_until_complete(set_hook())
        finally:
            loop.close()
            
        return f"Webhook set to: {url}/webhook"
    return "Please provide ?url=YOUR_VERCEL_URL"

def run_flask(): 
    app.run(port=5001, debug=False, use_reloader=False)

if __name__ == '__main__':
    print(">>> LOADING BOT (LOCAL MODE) <<< ")
    
    # Untuk local testing, kita bisa pakai polling biasa dengan satu app global
    local_bot_app = create_app()
    local_bot_app.add_handler(CommandHandler("start", start))
    local_bot_app.add_handler(CommandHandler("ctk_lap_mitra", ctk_lap_mitra))
    local_bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    local_bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_all_messages))
    
    # Jalankan Flask di thread terpisah agar polling tidak terblokir
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Starting polling...")
    local_bot_app.run_polling(drop_pending_updates=True)
