# Instagram Yuklovchi Telegram Bot - O'rnatish Qo'llanmasi

Professional Instagram kontent yuklovchi bot. @savedinstabot ga o'xshash.

## 📋 Talablar

- Python 3.8 yoki yuqori versiya
- FFmpeg (musiqa ajratish uchun)
- Telegram Bot Token (@BotFather dan)

## 🚀 O'rnatish Bosqichlari

### 1-Qadam: Python Kutubxonalarini O'rnatish

Terminalda quyidagi buyruqlarni bajaring:

```bash
cd instagram_bot
pip install -r requirements.txt
```

Bu quyidagi kutubxonalarni o'rnatadi:
- python-telegram-bot - Telegram bot uchun
- yt-dlp - Instagram yuklab olish uchun
- ffmpeg-python - Musiqa ajratish uchun
- va boshqalar

### 2-Qadam: FFmpeg O'rnatish

FFmpeg musiqa ajratish uchun zarur!

**Windows uchun:**

**Usul 1: Chocolatey orqali (Oson)**
```bash
choco install ffmpeg
```

**Usul 2: Qo'lda o'rnatish**
1. https://ffmpeg.org/download.html dan yuklab oling
2. Arxivni ochib oling
3. FFmpeg `bin` papkasini system PATH ga qo'shing
4. Tekshirish: `ffmpeg -version`

**Linux (Ubuntu/Debian) uchun:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3-Qadam: Bot Tokenni Tekshirish

`.env` faylini sozlang (tokeningizni kiriting):
```
BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_telegram_user_id
```

## ▶️ Botni Ishga Tushirish

```bash
cd instagram_bot
python bot.py
```

Agar hammasi to'g'ri bo'lsa, terminal "Bot started!" deb ko'rsatadi.

## 📱 Botdan Foydalanish

1. Telegram'da botingizni oching
2. `/start` buyrug'ini yuboring
3. Instagram'dan istalgan linkni nusxalang:
   - Reels: `https://instagram.com/reel/xxxxx`
   - Post: `https://instagram.com/p/xxxxx`
   - Story: `https://instagram.com/stories/xxxxx`
   - IGTV: `https://instagram.com/tv/xxxxx`

4. Linkni botga yuboring
5. Yuklab olish formatini tanlang:
   - 🎥 **Video** - Video yuklab olish
   - 🎵 **Musiqa** - Musiqani MP3 sifatida olish
   - 📷 **Foto** - Rasmni yuklab olish

## 🎯 Buyruqlar

- `/start` - Botni boshlash
- `/help` - Yordam va ko'rsatmalar
- `/language` - Tilni o'zgartirish (O'zbek/Rus/Ingliz)

## ⚙️ Sozlamalar

`.env` faylini tahrirlash orqali sozlashingiz mumkin:

```env
# Bot Token (@BotFather dan)
BOT_TOKEN=sizning_bot_tokeningiz

# Telegram Chat ID
ADMIN_CHAT_ID=sizning_chat_id

# Yuklab olish papkasi
DOWNLOAD_DIR=downloads

# Maksimal fayl hajmi (50MB - Telegram chegarasi)
MAX_FILE_SIZE=50000000

# Standart til (uz/ru/en)
DEFAULT_LANGUAGE=uz
```

## ❗ Muhim Eslatmalar

1. **Telegram Fayl Hajmi**: Maksimal 50MB
2. **Shaxsiy Akkauntlar**: Faqat ochiq akkauntlardan yuklab olish mumkin
3. **FFmpeg Kerak**: Musiqa ajratish uchun FFmpeg o'rnatilgan bo'lishi shart
4. **Instagram Cheklovlari**: Ba'zi kontentlar cheklangan bo'lishi mumkin

## 🔧 Muammolarni Hal Qilish

### Bot ishlamayapti
- `.env` faylidagi bot token to'g'riligini tekshiring
- Barcha kutubxonalar o'rnatilganligini tekshiring: `pip install -r requirements.txt`

### Musiqa ajratilmayapti
- FFmpeg o'rnatilganligini tekshiring: `ffmpeg -version`
- FFmpeg system PATH da borligini tekshiring

### Yuklab olish xato beradi
- Instagram linki to'g'ri va ochiq ekanligini tekshiring
- Kontent o'chirilgan yoki cheklangan bo'lishi mumkin

### "Fayl juda katta" xatosi
- Telegram 50MB dan katta fayllarni qabul qilmaydi
- Qisqaroq video yoki past sifatni tanlang

## 🎉 Tayyor!

Botingiz ishga tayyor! Istalgan Instagram linkini yuboring va yuklab oling!

## 📞 Yordam

Muammolar yuzaga kelsa, yuqoridagi "Muammolarni Hal Qilish" bo'limiga qarang.

---

**Omad! Botingizdan bahramand bo'ling! 🚀**
