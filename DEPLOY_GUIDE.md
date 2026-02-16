# Instagram Downloader & Music Search Bot - Deployment Guide

Ushbu qo'llanma botni Linux (Ubuntu) VPS serveriga doimiy (24/7) ishlatish uchun chiqarishga yordam beradi.

## 1. Serverni tayyorlash
Birinchi navbatda serveringizni yangilang va kerakli paketlarni o'rnating:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv ffmpeg git -y
```

## 2. Bot kodlarini yuklash
Bot kodlarini serverga joylashtiring. Agar GitHub ishlatsangiz:

```bash
git clone YOUR_REPOSITORY_URL
cd instagram_bot
```

Yoki fayllarni SFTP orqali yuklang va shu papkaga kiring.

## 3. Virtual muhit va Kutubxonalar
Bot uchun alohida muhit yarating va kutubxonalarni o'rnating:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Konfiguratsiya (.env)
`.env` faylini yarating va bot tokeningizni kiriting:

```bash
nano .env
```
Fayl ichiga quyidagilarni yozing:
```env
BOT_TOKEN=7637789321:AAHp_NpaqCJnlmVmXPh0OtioJme8wDhJ5ZA
ADMIN_CHAT_ID=5657790788
DOWNLOAD_DIR=downloads
```
(`Ctrl+O`, `Enter`, `Ctrl+X` tugmalari orqali saqlang).

## 5. Systemd Servis yaratish (Doimiy ishlash uchun)
Server o'chib yonsa ham bot o'zi yonishi va fonda ishlashi uchun servis yarating:

```bash
sudo nano /etc/systemd/system/instabot.service
```

Quyidagi matnni nusxalab qo'ying (papkalar yo'lini o'zingizga moslang):

```ini
[Unit]
Description=Instagram Downloader Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/instagram_bot
ExecStart=/root/instagram_bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 6. Servisni faollashtirish
```bash
sudo systemctl daemon-reload
sudo systemctl enable instabot
sudo systemctl start instabot
```

## 7. Holatni tekshirish
Bot ishlayotganini ko'rish uchun:
```bash
sudo systemctl status instabot
```
Loglarni ko'rish uchun:
```bash
journalctl -u instabot -f
```

---
**Tabriklayman!** Botingiz endi serverda 24/7 rejimida ishlamoqda. ✨🚀
