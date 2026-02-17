"""
Multi-platform Downloader Telegram Bot
Main bot application
"""
import socket
import sys
import _socket
import asyncio
import threading

# --- HYPER-NUCLEAR STATIC DNS PATCH (Redundant Layers) ---
def get_static_addrinfo(host, port):
    # DC4 IP for api.telegram.org
    ip = "149.154.167.220"
    try: p = int(port)
    except: p = 443
    # print(f"🎯 HYPER-DNS REDIRECT: {host} -> {ip}:{p}")
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, p))]

# 1. Base socket patch
_real_getaddrinfo = _socket.getaddrinfo
_real_gethostbyname = socket.gethostbyname
_real_getnameinfo = socket.getnameinfo

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host and isinstance(host, str) and 'telegram.org' in host:
        return get_static_addrinfo(host, port)
    return _real_getaddrinfo(host, port, family, type, proto, flags)

def patched_gethostbyname(host):
    if host and isinstance(host, str) and 'telegram.org' in host:
        # print(f"🎯 HYPER-DNS (hostbyname) REDIRECT: {host}")
        return "149.154.167.220"
    return _real_gethostbyname(host)

_socket.getaddrinfo = patched_getaddrinfo
socket.getaddrinfo = patched_getaddrinfo
socket.gethostbyname = patched_gethostbyname

# 2. Asyncio loop patch (for already initialized loops)
_real_loop_getaddrinfo = asyncio.BaseEventLoop.getaddrinfo
async def patched_loop_getaddrinfo(self, host, port, *args, **kwargs):
    if host and isinstance(host, str) and 'telegram.org' in host:
        return get_static_addrinfo(host, port)
    return await _real_loop_getaddrinfo(self, host, port, *args, **kwargs)
asyncio.BaseEventLoop.getaddrinfo = patched_loop_getaddrinfo

# 3. Anyio patch (Used by httpx/httpcore)
try:
    import anyio._core._sockets as anyio_sockets
    _real_anyio_getaddrinfo = anyio_sockets.getaddrinfo
    async def patched_anyio_getaddrinfo(host, port, *args, **kwargs):
        if host and isinstance(host, str) and 'telegram.org' in host:
            return get_static_addrinfo(host, port)
        return await _real_anyio_getaddrinfo(host, port, *args, **kwargs)
    anyio_sockets.getaddrinfo = patched_anyio_getaddrinfo
except Exception: pass

# print("🚀 HYPER-NUCLEAR DNS Patch Active (Multi-Layer).")
# --- END PATCH ---

import logging
import os

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

# Suppress httpx and telegram logs to prevent token leakage
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Add local bin to PATH for FFmpeg
local_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
if os.path.exists(local_bin):
    os.environ['PATH'] = local_bin + os.pathsep + os.environ.get('PATH', '')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    filters,
    ContextTypes,
)

from config import Config
from messages import get_message
from keyboards import Keyboards
from utils import is_valid_url, get_content_type, cleanup_file, is_file_too_large, clean_song_title, get_file_size
from downloader import InstagramDownloader
from audio_extractor import AudioExtractor
from database import Database
from audio_features import audio_features
from rate_limiter import rate_limiter

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)

# Initialize components
downloader = InstagramDownloader()
audio_extractor = AudioExtractor()
db = Database()

# User data storage
user_data_store = {}

# Global state for throttled updates
progress_update_tracker = {} # {query_id: last_update_time}

def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    return str(user_id) in Config.ADMIN_IDS or str(user_id) == Config.ADMIN_CHAT_ID

def get_progress_bar(percent):
    """Generate a text progress bar"""
    filled = int(percent / 10)
    return '▓' * filled + '░' * (10 - filled)

async def throttled_progress_update(query, text, force=False):
    """Update message with throttling to avoid Telegram rate limits"""
    import time
    query_id = str(query.id) if hasattr(query, 'id') else str(id(query))
    now = time.time()
    last_update = progress_update_tracker.get(query_id, 0)
    
    if force or (now - last_update >= 3.0): # Update every 3 seconds
        progress_update_tracker[query_id] = now
        try:
            await query.edit_message_text(text, parse_mode='HTML')
        except Exception:
            pass

def create_progress_hook(query, base_text):
    """Create a progress hook for yt-dlp"""
    def hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%', '')
                try: percent = float(p)
                except: percent = 0.0
                bar = get_progress_bar(percent)
                text = f"{base_text}\n[{bar}] {percent}%"
                
                # Check if we can run async in sync hook
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(throttled_progress_update(query, text), loop)
            except: pass
    return hook

async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is subscribed to the required channel (Bypassed for now)"""
    return True # Simple fix: Allow everyone

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command and referrals"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Handle Referral
    referred_by = None
    if context.args and context.args[0].startswith('ref_'):
        try:
            referrer_id = int(context.args[0].replace('ref_', ''))
            if referrer_id != user.id:
                referred_by = referrer_id
        except: pass

    # Add user with referral info
    db.add_user(user.id, user.username, user.first_name, user.last_name, referred_by=referred_by)
    if referred_by:
        if db.add_referral(user.id, referred_by):
            # Notify referrer
            try:
                referrer_lang = db.get_user_language(referred_by)
                msg = get_message(referrer_lang, 'referral_text').split('\n')[0] # Get header
                await context.bot.send_message(
                    chat_id=referred_by,
                    text=f"🎉 <b>Sizda yangi referral!</b>\n\n👤 {user.first_name} qo'shildi.\n💰 Hisobingizga <b>500 so'm</b> qo'shildi!",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Failed to notify referrer {referred_by}: {e}")

    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return

    await update.message.reply_text(get_message(lang, 'start'), reply_markup=Keyboards.main_menu(lang))
    logger.info(f"User {user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return
    await update.message.reply_text(get_message(lang, 'help'), parse_mode='HTML')

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return
    await update.message.reply_text(get_message(lang, 'choose_language'), reply_markup=Keyboards.language_selection())

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command (Admin only)"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return

    if not is_admin(user.id):
        return
    
    stats = db.get_admin_stats()
    await update.message.reply_text(
        get_message(lang, 'admin_stats').format(
            total_users=stats.get('total_users', 0),
            total_downloads=stats.get('total_downloads', 0),
            today_downloads=stats.get('today_downloads', 0)
        ),
        parse_mode='HTML'
    )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command (Admin only)"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return

    if not is_admin(user.id):
        return
    
    # Broadcast cooldown check
    if not rate_limiter.check_broadcast():
        cooldown = rate_limiter.get_broadcast_cooldown()
        await update.message.reply_text(f"⏳ Broadcast cooldown! {cooldown // 60} daqiqa kutish kerak.")
        return
    
    if not context.args and not update.message.caption:
        await update.message.reply_text("📢 Iltimos, xabar yozing yoki rasm/video bilan birga yuboring.")
        return
    
    message = " ".join(context.args) if context.args else update.message.caption or ""
    media = None
    media_type = 'text'
    
    if update.message.photo:
        media = update.message.photo[-1].file_id
        media_type = 'photo'
    elif update.message.video:
        media = update.message.video.file_id
        media_type = 'video'
        
    count = await run_broadcast(context.bot, message, media, media_type)
    await update.message.reply_text(f"✅ Xabar {count} ta foydalanuvchiga yuborildi.")

async def run_broadcast(bot, message: str, media=None, media_type: str = 'text') -> int:
    """Send message/media to all users"""
    users = db.get_all_users()
    count = 0
    for user_id in users:
        try:
            if media_type == 'text':
                await bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
            elif media_type == 'photo':
                await bot.send_photo(chat_id=user_id, photo=media, caption=message, parse_mode='HTML')
            elif media_type == 'video':
                await bot.send_video(chat_id=user_id, video=media, caption=message, parse_mode='HTML')
            count += 1
            await asyncio.sleep(0.05) # Rate limiting
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
    return count

async def handle_trending(query, user, lang, context):
    """Handle trending music display"""
    trending = db.get_trending_music(limit=10)
    if not trending:
        await query.edit_message_text("😔 Hozircha trendlar mavjud emas. Ko'proq musiqa yuklang!", reply_markup=Keyboards.back_button(lang))
        return
    
    text = "🔥 <b>Haftalik Trendlar:</b>\n\n"
    for i, (title, url, count) in enumerate(trending, 1):
        text += f"{i}. <b>{title}</b> — {count} yuklanish\n📎 <code>{url}</code>\n\n"
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=Keyboards.back_button(lang))

async def handle_recent_callback(query, user, lang, context):
    """Handle recent downloads display"""
    recent = db.get_recent_downloads(user.id, limit=5)
    if not recent:
        await query.edit_message_text("🕒 <b>Tarixingiz bo'sh.</b> Musiqa yoki video yuboring!", parse_mode='HTML', reply_markup=Keyboards.back_button(lang))
        return
    
    text = "🕒 <b>Sizning so'nggi yuklamalaringiz:</b>\n\n"
    for url, title, content_type, date in recent:
        icon = '🎥' if content_type == 'video' else '🎵'
        text += f"{icon} <b>{title}</b>\n📎 <code>{url}</code>\n\n"
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=Keyboards.back_button(lang))

async def check_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to check bot's permissions in the channel"""
    user = update.effective_user
    if not is_admin(user.id):
        return
    
    status_msg = f"🔍 <b>Diagnostika:</b>\n\n📌 Kanal: {Config.REQUIRED_CHANNEL}\n"
    
    try:
        chat = await context.bot.get_chat(chat_id=Config.REQUIRED_CHANNEL)
        status_msg += f"✅ Kanal topildi: <b>{chat.title}</b>\n"
        status_msg += f"🆔 Chat ID: <code>{chat.id}</code>\n"
        
        me = await context.bot.get_me()
        member = await context.bot.get_chat_member(chat_id=Config.REQUIRED_CHANNEL, user_id=me.id)
        status_msg += f"🤖 Bot statusi: <b>{member.status}</b>\n"
        
        if member.status in ['administrator', 'creator']:
            status_msg += "✅ Bot admin statusiga ega.\n"
        else:
            status_msg += "❌ <b>Muammo:</b> Bot kanalda admin emas! Tekshirish ishlamaydi.\n"
            
    except Exception as e:
        status_msg += f"❌ <b>Xatolik:</b> {e}\n"
        if "Member list is inaccessible" in str(e):
            status_msg += "\n💡 <b>Yechim:</b> Botni kanalda admin qiling!"
            
    await update.message.reply_text(status_msg, parse_mode='HTML')

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return

    if not context.args:
        await update.message.reply_text("❕ Foydalanish: /profile [username]")
        return
    
    username = context.args[0].replace('@', '')
    await update.message.reply_text(get_message(lang, 'downloading'))
    
    try:
        result = await downloader.download_profile_pic(username)
        if result and os.path.exists(result['filepath']):
            with open(result['filepath'], 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=f"👤 @{username} profile picture (HD)")
            cleanup_file(result['filepath'])
        else:
            await update.message.reply_text(get_message(lang, 'not_found'))
    except Exception as e:
        logger.error(f"Error in profile command: {e}")
        await update.message.reply_text(get_message(lang, 'error'))

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    # if not await is_subscribed(user.id, context):
    #     await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
    #     return
    auto_audio = db.get_user_auto_audio(user.id)
    status_text = get_message(lang, 'on') if auto_audio else get_message(lang, 'off')
    await update.message.reply_text(
        get_message(lang, 'settings').format(auto_audio=status_text),
        reply_markup=Keyboards.settings(auto_audio, lang),
        parse_mode='HTML'
    )

async def my_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /my_stats command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    # if not await is_subscribed(user.id, context):
    #     await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
    #     return
    stats = db.get_user_stats(user.id)
    await update.message.reply_text(
        get_message(lang, 'my_stats').format(
            total=stats['total_downloads'],
            music=stats['downloads_by_type'].get('youtube_music', 0),
            video=stats['downloads_by_type'].get('video', 0),
            photo=stats['downloads_by_type'].get('photo', 0)
        ),
        parse_mode='HTML'
    )

async def recent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /recent command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    # if not await is_subscribed(user.id, context):
    #     await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
    #     return
    recent = db.get_recent_downloads(user.id, limit=5)
    
    if not recent:
        await update.message.reply_text(get_message(lang, 'not_found'))
        return
        
    history_list = ""
    for url, title, ctype, date in recent:
        display_name = title if title else url
        history_list += f"• {display_name} ({ctype.capitalize()}) - {date}\n"
        
    await update.message.reply_text(
        get_message(lang, 'recent_downloads').format(list=history_list),
        parse_mode='HTML',
        disable_web_page_preview=True
    )

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /top command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return
    top = db.get_top_downloads(limit=10)
    
    if not top:
        await update.message.reply_text(get_message(lang, 'not_found'))
        return
        
    top_list = ""
    for i, (title, count) in enumerate(top, 1):
        top_list += f"{i}. 🔥 {title} ({count})\n"
        
    await update.message.reply_text(
        get_message(lang, 'top_music').format(list=top_list),
        parse_mode='HTML',
        disable_web_page_preview=True
    )

async def fav_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fav command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return
    
    favorites = db.get_favorites(user.id)
    if not favorites:
        await update.message.reply_text(get_message(lang, 'no_favorites'))
        return
    
    fav_list = ""
    for i, (title, url) in enumerate(favorites, 1):
        fav_list += f"{i}. {title}\n🔗 {url}\n\n"
    
    await update.message.reply_text(
        get_message(lang, 'favorites_list').format(list=fav_list),
        parse_mode='HTML',
        disable_web_page_preview=True
    )

async def lyrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lyrics command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return

    if not context.args:
        await update.message.reply_text("❕ Foydalanish: /lyrics [musiqa nomi]")
        return
    
    query = " ".join(context.args)
    wait_msg = await update.message.reply_text("🔍 Matn qidirilmoqda...")
    
    lyrics = await audio_features.get_lyrics(query)
    if lyrics:
        if len(lyrics) > 4000:
            lyrics = lyrics[:3000] + "..."
        await wait_msg.edit_text(f"🎤 <b>{query}</b> matni:\n\n{lyrics}", parse_mode='HTML')
    else:
        await wait_msg.edit_text("❌ Matn topilmadi.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice/audio messages for recognition"""
    logger.info(f"Voice message received from user {update.effective_user.id}")
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(get_message(lang, 'sub_required'), reply_markup=Keyboards.subscribe_keyboard(lang), parse_mode='HTML')
        return

    file = await update.message.voice.get_file() if update.message.voice else await update.message.audio.get_file()
    wait_msg = await update.message.reply_text("🎧 Musiqa tanilmoqda (Shazam)...")
    
    filepath = os.path.join(Config.DOWNLOAD_DIR, f"rec_{user.id}_{file.file_unique_id}.ogg")
    await file.download_to_drive(filepath)
    
    try:
        res = await audio_features.recognize_audio(filepath)
        if res:
            title, artist = res['title'], res['artist']
            await wait_msg.edit_text(f"✅ <b>Musiqa topildi!</b>\n\n🎵 <b>Nomi:</b> {title}\n👤 <b>Ijrochi:</b> {artist}\n\n🔍 Variantlar qidirilmoqda...", parse_mode='HTML')
            
            # Use search_music_versions to get all options at once
            results = await downloader.search_music_versions(title, artist=artist)
            
            if results and results.get('original'):
                user_data_store[user.id] = {
                    'type': 'music_search_versions', 
                    'results': results, 
                    'song_title': title, 
                    'uploader': artist
                }
                available_versions = [k for k, v in results.items() if v is not None]
                text = f"✅ <b>Musiqa topildi!</b>\n\n🎵 <b>Nomi:</b> {title}\n👤 <b>Ijrochi:</b> {artist}\n"
                if res.get('genres'):
                    text += f"🏷 <b>Janrlar:</b> {', '.join(res['genres'])}\n"
                
                await wait_msg.edit_text(
                    text + "\n👇 Variantni tanlang:",
                    reply_markup=Keyboards.music_versions(results['original']['id'], lang, available_versions),
                    parse_mode='HTML'
                )
            else:
                await wait_msg.edit_text(f"✅ <b>Musiqa:</b> {artist} - {title}\n\n❌ Afsuski, yuklash uchun manba topilmadi.")
        else:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            kb = [[InlineKeyboardButton("🔍 Nomini yozib qidirish", switch_inline_query_current_chat="")]]
            await wait_msg.edit_text(
                "❌ <b>Musiqa tanilmadi.</b>\n\nEslatma: Shazam asosan studiyada yozilgan musiqalarni yaxshi taniydi. Ovozli xabar aniq bo'lmasa, bot uni tanimasligi mumkin.\n\n👇 Pastdagi tugmani bosing yoki musiqaning nomini yozib yuboring:", 
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode='HTML'
            )
    finally:
        cleanup_file(filepath)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with URLs or music search"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    message_text = update.message.text
    
    # Rate limiting check (admins are exempt)
    if not is_admin(user.id) and not rate_limiter.check_message(user.id):
        cooldown = rate_limiter.get_remaining_cooldown(user.id)
        await update.message.reply_text(
            f"⚠️ Juda ko'p so'rov! {cooldown} soniya kutib turing.",
            parse_mode='HTML'
        )
        return

    if context.user_data.get('awaiting_withdraw'):
        # Process withdrawal request
        card = message_text.strip().replace(" ", "")
        if len(card) >= 16:
            balance = db.get_user_balance(user.id)
            min_amount = 10000 # Configurable
            if balance >= min_amount:
                if db.add_withdrawal(user.id, balance, card):
                    await update.message.reply_text(get_message(lang, 'withdraw_success_msg').format(amount=balance), parse_mode='HTML')
                    # Notify Admin
                    admin_text = f"💰 <b>Yang yechish so'rovi!</b>\n\n👤 <b>User:</b> {user.first_name} (@{user.username})\n🆔 <b>ID:</b> {user.id}\n💵 <b>Summa:</b> {balance} so'm\n💳 <b>Karta:</b> <code>{card}</code>"
                    try: await context.bot.send_message(chat_id=Config.ADMIN_CHAT_ID, text=admin_text, parse_mode='HTML')
                    except: pass
                else:
                    await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos keyinroq urinib ko'ring.")
            else:
                await update.message.reply_text(get_message(lang, 'withdraw_min').format(min_amount=min_amount, balance=balance), parse_mode='HTML')
            context.user_data['awaiting_withdraw'] = False
            return
        else:
            await update.message.reply_text("❌ Karta raqami noto'g'ri! Iltimos, 16 ta raqamni kiriting.")
            return

    if context.user_data.get('awaiting_trim'):
        # Process trimming time range "00:10 00:30"
        times = message_text.strip().split()
        if len(times) == 2:
            try:
                def time_to_sec(t):
                    parts = t.split(':')
                    if len(parts) == 2: return int(parts[0]) * 60 + int(parts[1])
                    return int(parts[0])
                
                start_sec = time_to_sec(times[0])
                end_sec = time_to_sec(times[1])
                
                filepath = user_data_store[user.id].get('last_filepath')
                if filepath and os.path.exists(filepath):
                    wait_msg = await update.message.reply_text(get_message(lang, 'tool_processing'))
                    trimmed_path = await audio_features.trim_audio(filepath, start_sec, end_sec)
                    if trimmed_path:
                        with open(trimmed_path, 'rb') as f:
                            if trimmed_path.endswith('.mp4'):
                                await update.message.reply_video(video=f, caption=f"✂️ {times[0]} - {times[1]}")
                            else:
                                await update.message.reply_audio(audio=f, title=f"Trimmed {times[0]}-{times[1]}")
                        user_data_store[user.id]['last_filepath'] = trimmed_path
                        await update.message.reply_text(get_message(lang, 'tools_prompt'), reply_markup=Keyboards.tools_menu(trimmed_path, lang), parse_mode='HTML')
                        asyncio.create_task(delayed_cleanup(trimmed_path, 600))
                        await wait_msg.delete()
                    else:
                        await wait_msg.edit_text(get_message(lang, 'error'))
                else:
                    await update.message.reply_text(get_message(lang, 'not_found'))
            except Exception as e:
                logger.error(f"Trim error: {e}")
                await update.message.reply_text("❌ Xato format! Misol: 00:10 00:30")
            context.user_data['awaiting_trim'] = False
            return
        else:
            await update.message.reply_text("❌ Iltimos, boshlanish va tugash vaqtini yuboring. Misol: 00:10 00:30")
            return

    if is_valid_url(message_text):
        # Sanitize URL involves removing tracking params
        message_text = sanitize_url(message_text)
        
        # Check if it's a playlist (simple check for list= or playlist/ or albums/)
        is_playlist = 'list=' in message_text or '/playlist/' in message_text or '/album/' in message_text
        
        if is_playlist:
            wait_msg = await update.message.reply_text("📋 <b>Pleylist aniqlandi.</b> Barcha elementlar yuklanmoqda...", parse_mode='HTML')
            try:
                # Use yt-dlp to get all entries in the playlist
                entries = await downloader.get_playlist_entries(message_text)
                if not entries:
                    await wait_msg.edit_text("❌ Pleylistdan elementlar topilmadi.")
                    return
                
                await wait_msg.edit_text(f"📋 <b>Pleylist: {len(entries)} ta element.</b> Yuklash boshlandi...", parse_mode='HTML')
                for i, entry_url in enumerate(entries, 1):
                    # Process each entry as a separate URL
                    await auto_download_all(update, context, entry_url, lang, is_playlist_item=True)
                    if i % 5 == 0: await asyncio.sleep(2) # Avoid flood limits
                
                await wait_msg.edit_text(f"✅ <b>Pleylist yakunlandi!</b> {len(entries)} ta element qayta ishlandi.", parse_mode='HTML')
            except Exception as e:
                logger.error(f"Error processing playlist: {e}")
                await wait_msg.edit_text("❌ Pleylistni qayta ishlashda xatolik yuz berdi.")
        else:
            # Auto delivery: Trigger video/audio downloads in parallel
            user_id = user.id
            user_data_store[user_id] = {
                'url': message_text, 
                'content_type': get_content_type(message_text),
                'chat_id': update.effective_chat.id
            }
            await auto_download_all(update, context, message_text, lang)
    else:
        search_query = message_text.strip()
        if len(search_query) < 2: return
        wait_msg = await update.message.reply_text(get_message(lang, 'search_searching').format(query=search_query), parse_mode='HTML')
        results = await downloader.search_music(search_query, limit=10)
        
        if results:
            user_data_store[user.id] = {'type': 'music_search_list', 'results': results, 'query': search_query}
            await wait_msg.edit_text(
                get_message(lang, 'search_results_list').format(query=search_query) + "\n\n" + get_message(lang, 'select_song'),
                reply_markup=Keyboards.music_search_results(results, lang), parse_mode='HTML'
            )
        else:
            await wait_msg.edit_text(get_message(lang, 'music_not_found'))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    user = query.from_user
    lang = db.get_user_language(user.id)
    data = query.data
    
    try:
        await query.answer()
    except Exception:
        pass # Ignore query too old errors
    
    if data.startswith('lang_'):
        new_lang = data.split('_')[1]
        db.set_user_language(user.id, new_lang)
        await query.edit_message_text(get_message(new_lang, 'language_changed'))
    elif data == 'toggle_auto_audio':
        current = db.get_user_auto_audio(user.id)
        db.set_user_auto_audio(user.id, not current)
        status_text = get_message(lang, 'on') if not current else get_message(lang, 'off')
        await query.edit_message_text(
            get_message(lang, 'settings').format(auto_audio=status_text),
            reply_markup=Keyboards.settings(not current, lang), parse_mode='HTML'
        )
    elif data.startswith('sl_song_'): await handle_select_song(query, user, lang, data)
    elif data.startswith('sl_song_search_'): await handle_song_search_callback(query, user, lang, data)
    elif data.startswith('msv_'): await handle_music_version(query, user, lang, data)
    elif data.startswith('add_fav_'): await handle_add_favorite(query, user, lang, data)
    elif data == 'referral': await handle_referral(query, user, lang, context)
    elif data == 'wallet': await handle_wallet(query, user, lang, context)
    elif data == 'withdraw_start': await handle_withdraw_start(query, user, lang, context)
    elif data == 'check_sub': await handle_check_sub(query, user, lang, context)
    elif data == 'back_to_main':
        await query.edit_message_text(get_message(lang, 'start'), reply_markup=Keyboards.main_menu(lang))
    elif data == 'trending': await handle_trending(query, user, lang, context)
    elif data == 'recent': await handle_recent_callback(query, user, lang, context)
    elif data == 'set_lang': await query.edit_message_text("🌐 Tilni tanlang / Выберите язык / Select language:", reply_markup=Keyboards.language_selection())
    elif data == 'download_video': await download_video(query, user, lang)
    elif data == 'download_audio': await download_audio(query, user, lang)
    elif data == 'download_photo': await download_photo(query, user, lang)
    elif data == 'cancel': 
        try: await query.message.delete()
        except: await query.answer()
    elif data.startswith('tool_'): await handle_tool_callback(query, user, lang, data, context)

async def handle_check_sub(query, user, lang, context):
    """Handle callback to check subscription status"""
    if await is_subscribed(user.id, context):
        try:
            await query.edit_message_text(get_message(lang, 'sub_thank_you'), reply_markup=Keyboards.main_menu(lang), parse_mode='HTML')
        except: pass
        await query.answer("✅ Rahmat!", show_alert=False)
    else:
        await query.answer("❌ Siz hali guruhga a'zo bo'lmadingiz!", show_alert=True)

async def handle_referral(query, user, lang, context):
    """Handle callback for referral link"""
    count = db.get_referral_count(user.id)
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
    
    # Send as new message to ensure visibility and avoid edit errors
    try:
        await query.message.delete()
    except: pass
    
    await query.message.reply_text(
        get_message(lang, 'referral_text').format(link=referral_link, count=count),
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=Keyboards.back_button(lang)
    )

async def handle_wallet(query, user, lang, context):
    """Handle callback for wallet"""
    balance = db.get_user_balance(user.id)
    count = db.get_referral_count(user.id)
    await query.edit_message_text(
        get_message(lang, 'wallet_text').format(balance=balance, count=count),
        parse_mode='HTML',
        reply_markup=Keyboards.wallet(lang)
    )

async def handle_withdraw_start(query, user, lang, context):
    """Start withdrawal process"""
    balance = db.get_user_balance(user.id)
    min_amount = 10000 
    if balance < min_amount:
        await query.answer(f"❌ Minimal yechish miqdori: {min_amount} so'm!", show_alert=True)
        return
        
    context.user_data['awaiting_withdraw'] = True
    await query.edit_message_text(
        get_message(lang, 'withdraw_prompt'),
        parse_mode='HTML',
        reply_markup=Keyboards.withdraw_cancel(lang)
    )

async def handle_select_song(query, user, lang, data):
    """Handle song selection with parallel version search"""
    song_id = data.replace('sl_song_', '')
    if user.id not in user_data_store or user_data_store[user.id].get('type') != 'music_search_list':
        await query.edit_message_text(get_message(lang, 'error')); return
    
    selected_song = next((res for res in user_data_store[user.id]['results'] if res['id'] == song_id), None)
    if not selected_song: await query.edit_message_text(get_message(lang, 'error')); return
    
    cleaned_title = clean_song_title(selected_song['title'])
    artist_name = selected_song.get('uploader', '')
    await query.edit_message_text(get_message(lang, 'search_searching').format(query=f"{artist_name} {cleaned_title}"), parse_mode='HTML')
    results = await downloader.search_music_versions(cleaned_title, artist=artist_name)
    
    if results and results.get('original'):
        user_data_store[user.id] = {'type': 'music_search_versions', 'results': results, 'song_title': selected_song['title'], 'uploader': artist_name}
        available_versions = [k for k, v in results.items() if v is not None]
        # Use reply instead of edit to keep the search list accessible
        await query.message.reply_text(
            get_message(lang, 'search_results').format(title=selected_song['title']),
            reply_markup=Keyboards.music_versions(results['original']['id'], lang, available_versions), parse_mode='HTML'
        )
    else:
        await query.answer(get_message(lang, 'music_not_found'), show_alert=True)

async def handle_song_search_callback(query, user, lang, data):
    """Handle YouTube search from recognized song"""
    search_query = data.replace('sl_song_search_', '')
    await query.edit_message_text(get_message(lang, 'search_searching').format(query=search_query), parse_mode='HTML')
    results = await downloader.search_music(search_query, limit=10)
    
    if results:
        user_data_store[user.id] = {'type': 'music_search_list', 'results': results, 'query': search_query}
        await query.edit_message_text(
            get_message(lang, 'search_results_list').format(query=search_query) + "\n\n" + get_message(lang, 'select_song'),
            reply_markup=Keyboards.music_search_results(results, lang), parse_mode='HTML'
        )
    else:
        await query.edit_message_text(get_message(lang, 'music_not_found'))

async def handle_add_favorite(query, user, lang, data):
    """Handle adding song to favorites"""
    song_id = data.replace('add_fav_', '')
    if user.id not in user_data_store or 'song_title' not in user_data_store[user.id]:
        await query.answer(get_message(lang, 'error'))
        return
    
    title = user_data_store[user.id]['song_title']
    uploader = user_data_store[user.id].get('uploader', 'Bot')
    full_title = f"{uploader} - {title}"
    
    results = user_data_store[user.id].get('results', {})
    original = results.get('original', {})
    url = original.get('url', '') if original else ''
    
    if db.add_favorite(user.id, full_title, url):
        await query.answer(get_message(lang, 'favorite_added'), show_alert=True)
    else:
        await query.answer(get_message(lang, 'error'))

async def handle_music_version(query, user, lang, data):
    """Handle music version selection and download"""
    logger.info(f"Callback data received: {data}")
    parts = data.split('_')
    if len(parts) < 3:
        logger.error(f"Invalid callback data parts: {parts}")
        await query.edit_message_text(get_message(lang, 'error')); return
        
    if user.id not in user_data_store:
        logger.error(f"User {user.id} not in user_data_store")
        await query.edit_message_text(get_message(lang, 'error')); return
        
    if user_data_store[user.id].get('type') != 'music_search_versions':
        logger.error(f"Invalid session type for user {user.id}: {user_data_store[user.id].get('type')}")
        await query.edit_message_text(get_message(lang, 'error')); return
    
    version_type = parts[1]
    result = user_data_store[user.id]['results'].get(version_type)
    if not result:
        logger.error(f"Version {version_type} not found in results for user {user.id}")
        await query.edit_message_text(get_message(lang, 'music_not_found')); return
    
    logger.info(f"Downloading version {version_type} for user {user.id}: {result['url']}")
    
    # 1. Loading Animation (Use new message instead of editing versions menu)
    wait_text = get_message(lang, 'downloading')
    wait_msg = await query.message.reply_text(f"{wait_text}\n[░░░░░░░░░░] 0%", parse_mode='HTML')
    
    try:
        # Create real progress hook
        hook = create_progress_hook(query, wait_text)
        
        # Download with real hook
        download_result = await downloader.download_audio(result['url'], progress_hook=hook)
        
        # Retry logic if download fails
        if not download_result or not os.path.exists(download_result.get('filepath', '')):
            logger.info(f"Primary download failed for {result['url']}, trying fallback search...")
            try:
                await wait_msg.edit_text(f"{wait_text}\n[░░░░░░░░░░] 0% (Muqobil variant qidirilmoqda...)")
            except: pass
            
            search_query = f"{result['title']} {result.get('uploader', '')}"
            alternatives = await downloader.search_music(search_query, limit=5)
            
            if alternatives:
                for alt in alternatives:
                    if alt['url'] == result['url']: continue
                    
                    logger.info(f"Trying alternative: {alt['url']}")
                    download_result = await downloader.download_audio(alt['url'], progress_hook=hook)
                    if download_result and os.path.exists(download_result.get('filepath', '')):
                         result['url'] = alt['url'] # Update for DB
                         break

        if download_result and os.path.exists(download_result['filepath']):
            filepath = download_result['filepath']
            
            if is_file_too_large(filepath):
                cleanup_file(filepath); await wait_msg.edit_text(get_message(lang, 'file_too_large')); return
            
            # 2. Final Upload
            await throttled_progress_update(wait_msg, f"{get_message(lang, 'uploading')}\n[▓▓▓▓▓▓▓▓▓░] 90%", force=True)
            
            title = download_result.get('title', result['title'])
            performer = download_result.get('uploader', result['uploader'])
            
            with open(filepath, 'rb') as f:
                # Parallelize Audio upload and DB logging
                upload_res = await query.message.reply_audio(audio=f, title=title, performer=performer)
                try:
                    await asyncio.to_thread(db.add_download, user.id, result['url'], 'youtube_music', version_type, title, True)
                except Exception as de:
                    logger.error(f"DB log error: {de}")
            
            # Store last_filepath for tools menu
            user_data_store[user.id]['last_filepath'] = filepath
            # Show tools menu (Simplified tools menu call)
            await query.message.reply_text(
                get_message(lang, 'tools_prompt'),
                reply_markup=Keyboards.tools_menu(filepath, lang),
                parse_mode='HTML'
            )
            
            # Use delayed cleanup (defined at the end of file)
            asyncio.create_task(delayed_cleanup(filepath, 600)) 
            await wait_msg.edit_text(f"{get_message(lang, 'success')}\n[▓▓▓▓▓▓▓▓▓▓] 100%")
        else:
            logger.error(f"Download failed or file not found: {download_result}")
            await wait_msg.edit_text(get_message(lang, 'error'))
    except Exception as e:
        logger.error(f"Error handling music version: {e}", exc_info=True)
        if 'wait_msg' in locals(): await wait_msg.edit_text(get_message(lang, 'error'))

async def auto_download_all(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, lang: str, is_playlist_item: bool = False):
    """Automatically download and send media based on user preferences and availability"""
    wait_msg = None
    if not is_playlist_item:
        wait_msg = await update.message.reply_text(get_message(lang, 'downloading'))
    
    sent_something = False
    video_res = None
    
    # 1. Try Video First (usually what users want most)
    try:
        video_res = await downloader.download_video(url)
        if video_res and not isinstance(video_res, Exception):
            filepath = video_res['filepath']
            if os.path.exists(filepath):
                if not is_file_too_large(filepath):
                    if wait_msg: await wait_msg.edit_text(get_message(lang, 'uploading'))
                    title = video_res.get('title', '')
                    user_data_store[update.effective_user.id]['song_title'] = title
                    user_data_store[update.effective_user.id]['last_filepath'] = filepath
                    with open(filepath, 'rb') as f:
                        await update.message.reply_video(video=f, caption=title, supports_streaming=True, write_timeout=300, read_timeout=300, connect_timeout=300)
                    sent_something = True
                    db.add_download(update.effective_user.id, url, 'video', 'auto_video', title=title, success=True)
                    # Use delayed cleanup instead of immediate
                    asyncio.create_task(delayed_cleanup(filepath, 600))
                else:
                    await update.message.reply_text(get_message(lang, 'file_too_large'))
                    cleanup_file(filepath)
    except Exception as e:
        logger.error(f"Auto video error for {url}: {e}")

    # 2. Try Audio if Video failed OR if Auto-Audio is enabled OR if it is Instagram (Force Dual)
    auto_audio = db.get_user_auto_audio(update.effective_user.id)
    platform = get_content_type(url)
    
    if not sent_something or auto_audio or platform == 'instagram':
        try:
            # Special logic for Instagram "Full Audio"
            if platform == 'instagram' and not is_playlist_item:
                if wait_msg: await wait_msg.edit_text("🎵 To'liq musiqa qidirilmoqda...")
                # Try to extract music info first
                try:
                    import yt_dlp
                    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                        info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                        track = info.get('track')
                        artist = info.get('artist')
                        if track and artist:
                            search_res = await downloader.search_music(f"{artist} {track}", limit=1)
                            if search_res:
                                url = search_res[0]['url']
                                if wait_msg: await wait_msg.edit_text(f"🎵 <b>{artist} - {track}</b> topildi. Yuklanmoqda...")
                except: pass

            audio_res = await downloader.download_audio(url)
            if audio_res and not isinstance(audio_res, Exception) and os.path.exists(audio_res['filepath']):
                if not is_file_too_large(audio_res['filepath']):
                    title = audio_res.get('title', 'Audio')
                    performer = audio_res.get('uploader', 'Bot')
                    user_data_store[update.effective_user.id]['song_title'] = title
                    user_data_store[update.effective_user.id]['uploader'] = performer
                    user_data_store[update.effective_user.id]['last_filepath'] = audio_res['filepath']
                    with open(audio_res['filepath'], 'rb') as f:
                        await update.message.reply_audio(audio=f, title=title, performer=performer, write_timeout=300, read_timeout=300, connect_timeout=300)
                    sent_something = True
                    db.add_download(update.effective_user.id, url, 'audio', 'auto_audio', title=title, success=True)
                    asyncio.create_task(delayed_cleanup(audio_res['filepath'], 600))
                else:
                    await update.message.reply_text(get_message(lang, 'file_too_large'))
                    cleanup_file(audio_res['filepath'])
        except Exception as e:
            logger.error(f"Auto audio error for {url}: {e}")

    if sent_something:
        if wait_msg: await wait_msg.delete()
        try:
            last_file = user_data_store[update.effective_user.id].get('last_filepath')
            if last_file:
                await update.message.reply_text(
                    get_message(lang, 'tools_prompt'),
                    reply_markup=Keyboards.tools_menu(last_file, lang),
                    parse_mode='HTML'
                )
        except: pass
    else:
        # Check for photo as last resort
        try:
            photo_res = await downloader.download_photo(url)
            if photo_res and os.path.exists(photo_res['filepath']):
                title = photo_res.get('title', 'Photo')
                with open(photo_res['filepath'], 'rb') as f:
                    await update.message.reply_photo(photo=f, caption=title)
                cleanup_file(photo_res['filepath'])
                if wait_msg: await wait_msg.delete()
            else:
                if wait_msg: await wait_msg.edit_text(get_message(lang, 'not_found'))
                else: await update.message.reply_text(get_message(lang, 'not_found'))
        except Exception as e:
            logger.error(f"Auto photo error for {url}: {e}")
            if wait_msg: await wait_msg.edit_text(get_message(lang, 'error'))
            else: await update.message.reply_text(get_message(lang, 'error'))

async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline search queries"""
    query = update.inline_query.query
    if not query or len(query) < 2: return
    
    results = await downloader.search_music(query, limit=10)
    if not results: return
    
    inline_results = []
    from telegram import InlineQueryResultArticle, InputTextMessageContent
    
    for i, res in enumerate(results):
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),
                title=res['title'],
                description=f"🎵 {res.get('uploader', 'Music')}",
                thumbnail_url=res.get('thumbnail'),
                input_message_content=InputTextMessageContent(res['url'])
            )
        )
    
    await update.inline_query.answer(inline_results, cache_time=300)

async def handle_tool_callback(query, user, lang, data, context):
    """Handle media processing tools callbacks"""
    filepath = user_data_store[user.id].get('last_filepath')
    if not filepath or not os.path.exists(filepath):
        await query.answer(get_message(lang, 'not_found'), show_alert=True)
        return

    if data == 'tool_trim_init':
        context.user_data['awaiting_trim'] = True
        await query.edit_message_text(get_message(lang, 'tool_trim_prompt'), parse_mode='HTML', reply_markup=Keyboards.cancel_button(lang))
    
    elif data == 'tool_voice_conv':
        wait_msg = await query.edit_message_text(get_message(lang, 'tool_processing'))
        from utils import convert_to_voice
        voice_path = await convert_to_voice(filepath)
        if voice_path:
            with open(voice_path, 'rb') as f:
                await query.message.reply_voice(voice=f)
            # Store last_filepath for chained tools
            user_data_store[user.id]['last_filepath'] = voice_path
            await query.message.reply_text(get_message(lang, 'tools_prompt'), reply_markup=Keyboards.tools_menu(voice_path, lang), parse_mode='HTML')
            asyncio.create_task(delayed_cleanup(voice_path, 600))
            await wait_msg.delete()
        else:
            await wait_msg.edit_text(get_message(lang, 'error'))

    elif data == 'tool_mute_vid':
        wait_msg = await query.edit_message_text(get_message(lang, 'tool_processing'))
        from utils import mute_video
        muted_path = await mute_video(filepath)
        if muted_path:
            with open(muted_path, 'rb') as f:
                await query.message.reply_video(video=f, caption="🔇 Ovoz o'chirildi")
            user_data_store[user.id]['last_filepath'] = muted_path
            await query.message.reply_text(get_message(lang, 'tools_prompt'), reply_markup=Keyboards.tools_menu(muted_path, lang), parse_mode='HTML')
            asyncio.create_task(delayed_cleanup(muted_path, 600))
            await wait_msg.delete()
        else:
            await wait_msg.edit_text(get_message(lang, 'error'))

    elif data == 'tool_speed_init':
        await query.edit_message_text(get_message(lang, 'tool_speed_prompt'), reply_markup=Keyboards.speed_options(lang))

    elif data.startswith('tool_speed_set_'):
        speed = float(data.split('_')[-1])
        wait_msg = await query.edit_message_text(get_message(lang, 'tool_processing'))
        from utils import change_video_speed
        speed_path = await change_video_speed(filepath, speed)
        if speed_path:
            with open(speed_path, 'rb') as f:
                await query.message.reply_video(video=f, caption=f"⚡ Tezlik: {speed}x")
            user_data_store[user.id]['last_filepath'] = speed_path
            await query.message.reply_text(get_message(lang, 'tools_prompt'), reply_markup=Keyboards.tools_menu(speed_path, lang), parse_mode='HTML')
            asyncio.create_task(delayed_cleanup(speed_path, 600))
            await wait_msg.delete()
        else:
            await wait_msg.edit_text(get_message(lang, 'error'))

    elif data == 'tool_lyrics_get':
        wait_msg = await query.edit_message_text("🔍 <b>Matn qidirilmoqda...</b>", parse_mode='HTML')
        title = user_data_store[user.id].get('song_title', os.path.basename(filepath).split('.')[0])
        artist = user_data_store[user.id].get('uploader', '')
        lyrics = await audio_features.get_lyrics(title, artist)
        if lyrics:
            if len(lyrics) > 4000: lyrics = lyrics[:3000] + "..."
            await wait_msg.edit_text(f"📝 <b>{title}</b> matni:\n\n{lyrics}", parse_mode='HTML')
        else:
            await wait_msg.edit_text("❌ Matn topilmadi.")

    elif data == 'tool_lyrics_card':
        wait_msg = await query.edit_message_text("🖼 <b>Matnli rasm tayyorlanmoqda...</b>", parse_mode='HTML')
        title = user_data_store[user.id].get('song_title', os.path.basename(filepath).split('.')[0])
        artist = user_data_store[user.id].get('uploader', '')
        lyrics = await audio_features.get_lyrics(title, artist)
        if lyrics:
            from utils import generate_lyrics_card
            card_path = await generate_lyrics_card(lyrics, title, artist)
            if card_path:
                with open(card_path, 'rb') as f:
                    await query.message.reply_photo(photo=f, caption=f"🎶 <b>{title}</b> matni")
                cleanup_file(card_path)
                await wait_msg.delete()
            else:
                await wait_msg.edit_text("❌ Rasm tayyorlashda xatolik.")
        else:
            await wait_msg.edit_text("❌ Matn topilmadi.")

    elif data == 'tool_translate':
        wait_msg = await query.edit_message_text("🌐 <b>Tarjima qilinmoqda...</b>", parse_mode='HTML')
        text_to_translate = user_data_store[user.id].get('song_title', os.path.basename(filepath).split('.')[0])
        from utils import translate_text
        translated = await translate_text(text_to_translate, target_lang=lang)
        if translated and translated != text_to_translate:
            await wait_msg.edit_text(f"🌐 <b>Tarjima ({lang}):</b>\n\n{translated}", parse_mode='HTML')
        else:
            await wait_msg.edit_text("❌ Tarjima qilishning imkoni bo'lmadi yoki matn allaqachon shu tilda.")

    elif data == 'tool_summary':
        wait_msg = await query.edit_message_text("📊 <b>Video taxlil qilinmoqda...</b>", parse_mode='HTML')
        url = user_data_store[user.id].get('url')
        if not url:
            await wait_msg.edit_text("❌ URL topilmadi.")
            return
        
        from ai_tools import ai_tools
        summary = await ai_tools.get_youtube_summary(url)
        if summary:
            await wait_msg.edit_text(summary, parse_mode='HTML', reply_markup=Keyboards.back_button(lang))
        else:
            await wait_msg.edit_text("❌ Xulosa tayyorlash imkoni bo'lmadi.")

    elif data == 'premium_menu':
        is_prem = db.is_premium(user.id)
        status = "✅ Faol" if is_prem else "❌ Faol emas"
        text = f"💎 <b>Premium Status:</b> {status}\n\nPremium bilan yanada ko'proq imkoniyatlarga ega bo'ling!"
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=Keyboards.premium_menu(lang))

    elif data.startswith('buy_prem_'):
        days = int(data.split('_')[-1])
        db.set_premium(user.id, True, days=days)
        await query.answer("🎉 Premium muvaffaqiyatli faollashtirildi!", show_alert=True)
        await query.edit_message_text("✅ <b>Tabriklaymiz!</b> Endi siz Premium foydalanuvchisiz.", parse_mode='HTML', reply_markup=Keyboards.main_menu(lang))

    elif data == 'tool_effects_init':
        await query.edit_message_text("🪄 <b>Ovoz effektini tanlang:</b>", parse_mode='HTML', reply_markup=Keyboards.audio_effects(lang))

    elif data.startswith('tool_effect_'):
        effect = data.replace('tool_effect_', '')
        wait_msg = await query.edit_message_text(get_message(lang, 'tool_processing'))
        
        # Apply effect
        effect_path = await audio_features.apply_effect(filepath, effect)
        if effect_path:
            title = user_data_store[user.id].get('song_title', 'Audio')
            performer = user_data_store[user.id].get('uploader', 'Bot')
            
            # Map effect name for caption
            effect_names = {'bass_boost': '🔊 Bass Boost', '8d': '🎧 8D Version', 'slowed_reverb': '🌙 Slowed'}
            caption = f"{effect_names.get(effect, 'Magic')} ✨"
            
            with open(effect_path, 'rb') as f:
                await query.message.reply_audio(audio=f, title=title, performer=performer, caption=caption)
            
            # Update last_filepath for chained tools
            user_data_store[user.id]['last_filepath'] = effect_path
            await query.message.reply_text(get_message(lang, 'tools_prompt'), reply_markup=Keyboards.tools_menu(effect_path, lang), parse_mode='HTML')
            asyncio.create_task(delayed_cleanup(effect_path, 600))
            await wait_msg.delete()
        else:
            await wait_msg.edit_text(get_message(lang, 'error'))

    elif data == 'tool_back_to_tools':
        await query.edit_message_text(get_message(lang, 'tools_prompt'), reply_markup=Keyboards.tools_menu(filepath, lang), parse_mode='HTML')

async def download_video(query, user, lang):
    """Download video manually (still kept for backward compatibility if needed)"""
    if user.id not in user_data_store: await query.edit_message_text(get_message(lang, 'error')); return
    url = user_data_store[user.id]['url']
    await query.edit_message_text(get_message(lang, 'downloading'))
    
    try:
        result = await downloader.download_video(url)
        if result and os.path.exists(result['filepath']):
            filepath = result['filepath']
            if is_file_too_large(filepath):
                cleanup_file(filepath); await query.edit_message_text(get_message(lang, 'file_too_large')); return
            
            await query.edit_message_text(get_message(lang, 'uploading'))
            with open(filepath, 'rb') as f:
                await query.message.reply_video(video=f, caption=result.get('title', ''), supports_streaming=True)
            cleanup_file(filepath)
            db.add_download(user.id, url, user_data_store[user.id]['content_type'], 'video', True)
            await query.edit_message_text(get_message(lang, 'success'))
        else:
            await query.edit_message_text(get_message(lang, 'error'))
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await query.edit_message_text(get_message(lang, 'error'))

async def download_audio(query, user, lang):
    """Download audio from any supported platform"""
    if user.id not in user_data_store: await query.edit_message_text(get_message(lang, 'error')); return
    url = user_data_store[user.id]['url']
    await query.edit_message_text(get_message(lang, 'downloading'))
    
    try:
        result = await downloader.download_audio(url)
        if result and os.path.exists(result['filepath']):
            filepath = result['filepath']
            if is_file_too_large(filepath):
                cleanup_file(filepath); await query.edit_message_text(get_message(lang, 'file_too_large')); return
            
            await query.edit_message_text(get_message(lang, 'uploading'))
            with open(filepath, 'rb') as f:
                await query.message.reply_audio(audio=f, title=result.get('title', 'Audio'), performer=result.get('uploader', 'Bot'))
            cleanup_file(filepath)
            db.add_download(user.id, url, user_data_store[user.id]['content_type'], 'audio', True)
            await query.edit_message_text(get_message(lang, 'success'))
        else:
            await query.edit_message_text(get_message(lang, 'error'))
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        await query.edit_message_text(get_message(lang, 'error'))

async def download_photo(query, user, lang):
    """Download photo from any supported platform"""
    if user.id not in user_data_store: await query.edit_message_text(get_message(lang, 'error')); return
    url = user_data_store[user.id]['url']
    await query.edit_message_text(get_message(lang, 'downloading'))
    
    try:
        result = await downloader.download_photo(url)
        if result and os.path.exists(result['filepath']):
            filepath = result['filepath']
            if is_file_too_large(filepath):
                cleanup_file(filepath); await query.edit_message_text(get_message(lang, 'file_too_large')); return
            
            await query.edit_message_text(get_message(lang, 'uploading'))
            with open(filepath, 'rb') as f:
                await query.message.reply_photo(photo=f, caption=result.get('title', ''))
            cleanup_file(filepath)
            db.add_download(user.id, url, user_data_store[user.id]['content_type'], 'photo', True)
            await query.edit_message_text(get_message(lang, 'success'))
        else:
            await query.edit_message_text(get_message(lang, 'error'))
    except Exception as e:
        logger.error(f"Error downloading photo: {e}")
        await query.edit_message_text(get_message(lang, 'error'))

async def post_init(application: Application):
    """Set bot commands menu"""
    commands = [
        ("start", "Botni ishga tushirish / Start bot"),
        ("top", "Eng ko'p yuklangan musiqalar / Top music"),
        ("my_stats", "Mening statistikam / My stats"),
        ("recent", "Oxirgi yuklamalar / Recent downloads"),
        ("fav", "Saralanganlar / Favorites"),
        ("lyrics", "Musiqa matni / Lyrics"),
        ("settings", "Sozlamalar / Settings"),
        ("language", "Tilni o'zgartirish / Language"),
        ("help", "Yordam / Help"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    """Start the bot"""
    # Start health check server first
    try:
        from health_server import start_health_server
        start_health_server()
        logger.info("🌐 Health check server started successfully")
    except Exception as e:
        logger.warning(f"⚠️ Could not start health server: {e}")
        logger.warning("Bot will continue without health endpoint")
    
    # Token diagnostics (DO NOT log token values!)
    if not Config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is EMPTY! Check Hugging Face Secrets.")
    else:
        logger.info(f"✅ BOT_TOKEN loaded (Length: {len(Config.BOT_TOKEN)})")

    logger.info("📡 Relying on Multi-Layer DNS Monkeypatch for api.telegram.org")
    
    try:
        test_ip = socket.gethostbyname('api.telegram.org')
        logger.info(f"✅ DNS Patch verified: api.telegram.org -> {test_ip}")
    except Exception as e:
        logger.warning(f"⚠️ DNS Patch verification failed: {e}")

    # Configure HTTPXRequest with HTTP/1.1 to avoid connection issues
    from telegram.request import HTTPXRequest
    request = HTTPXRequest(
        connection_pool_size=10,
        connect_timeout=60.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=60.0,
        http_version="1.1"  # Force HTTP 1.1
    )

    application = Application.builder().token(Config.BOT_TOKEN).request(request).post_init(post_init).build()
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("my_stats", my_stats_command))
    application.add_handler(CommandHandler("recent", recent_command))
    application.add_handler(CommandHandler("fav", fav_command))
    application.add_handler(CommandHandler("lyrics", lyrics_command))
    application.add_handler(CommandHandler("check_admin", check_admin_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(InlineQueryHandler(handle_inline_query))
    print("✅ Bot ishladi! (Bot successfully started and ready)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def delayed_cleanup(filepath: str, delay: int = 600):
    """Cleanup file after a delay to allow tool usage"""
    await asyncio.sleep(delay)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Delayed cleanup removed: {filepath}")
    except Exception as e:
        logger.error(f"Error in delayed cleanup for {filepath}: {e}")

if __name__ == '__main__':
    main()
