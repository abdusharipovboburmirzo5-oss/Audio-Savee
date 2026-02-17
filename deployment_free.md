# 🚀 Botni Tekin Serverga Qo'yish (Deployment Guide)

Do'stim, mablag'ingiz bo'lmasa ham botni ishga tushirib, pul ishlashni boshlashingiz mumkin. Quyida eng yaxshi 3 ta tekin variantni tayyorladim.

## 1-Variant: Render.com (Tavsiya qilinadi!)
Render - botni 24/7 ishlatish uchun eng stabil va oson variant.

1. [dashboard.render.com](https://dashboard.render.com) ga kiring.
2. **"New +"** -> **"Web Service"** tugmasini bosing.
3. GitHub repozitoriyangizni ulang.
4. **Runtime**: `Docker` ni tanlang.
5. `BOT_TOKEN` va `ADMIN_CHAT_ID` ni **Environment Variables** ga qo'shing.

## 2-Variant: Hugging Face Spaces (Karta so'ramaydi!)
4. **License**: **Apache 2.0** deb tanlang.
5. **Repository**: Pastroqda "Connect your GitHub" tugmasini bosing va o'zingizning GitHub repozitoriyangizni (`Audio-Savee`) tanlang.
6. **Create Space** tugmasini bosing.
7. **Sozlash**: Space yaratilgandan so'ng, "Settings" bo'limiga kiring.
8. **Variables and secrets** bo'limida **"New secret"** tugmasini bosing:
   - Name: `BOT_TOKEN`
   - Value: (Bot tokeningizni yozing)
9. Bot avtomatik ishga tushadi!

## 2-Variant: Koyeb
Koyeb ham yaxshi, lekin ba'zida karta so'rab qoladi.

> [!WARNING]
> Koyeb-ning tekin versiyasida fayllar saqlanib qolmaydi. Bot o'chib yonsa, bazadagi ma'lumotlar o'chib ketishi mumkin. Buning uchun pastdagi "Ma'lumotlar bazasi" bo'limini o'qing.

## 2-Variant: Google Cloud (90 kunlik + doimiy tekin)
Google Cloud sizga boshida $300 bonus beradi (kartangiz bo'lishi shart, lekin pul yechmaydi).

1. **Google Cloud Console**-da `e2-micro` instance yarating.
2. Ubuntu serverini tanlang.
3. SSH orqali ulanib, bizni Docker-ni ishga tushiring.

## 3-Variant: Oracle Cloud (Eng zo'ri)
Agar karta topsangiz, Oracle **24GB RAM**-li serverni butunlay tekinga beradi. Bu bot uchun eng yaxshi "uy".

---

## 🔄 Health Check (Server Uyquga Ketmasligi Uchun)

Bepul serverlar 10-15 daqiqa faoliyat bo'lmasa uyquga ketadi. Buning oldini olish uchun **tashqi ping servis** ishlatamiz.

### UptimeRobot (Tavsiya qilinadi - 100% Tekin)

1. [uptimerobot.com](https://uptimerobot.com) saytiga kiring va ro'yxatdan o'ting
2. **"Add New Monitor"** tugmasini bosing
3. Quyidagi ma'lumotlarni kiriting:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: Instagram Bot Health
   - **URL**: Sizning bot URL-ingiz + `/health`
     - Hugging Face: `https://your-username-audio-save-bot.hf.space/health`
     - Render: `https://your-app-name.onrender.com/health`
   - **Monitoring Interval**: 5 minutes (tekin rejada)
4. **Create Monitor** tugmasini bosing

✅ Endi server har 5 daqiqada ping oladi va uyquga ketmaydi!

### Boshqa Variantlar

- **cron-job.org** - Har 1 daqiqada ping yuborish mumkin
- **Koyeb** - O'zida health check bor (sozlash shart emas)

### Health Check Endpoint-lar

Botingizda 3 ta endpoint mavjud:
- `/` - Bot holati va uptime
- `/health` - Monitoring uchun
- `/ping` - Oddiy ping

---

## 💾 Ma'lumotlar Bazasi (Persistence)

Tekin serverlar odatda fayllarni o'chirib yuboradi. Foydalanuvchilar balansini yo'qotmaslik uchun:
1. [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-free-tier) - 512MB tekin baza beradi.
2. [Aiven.io](https://aiven.io/postgresql) - Tekin PostgreSQL (bazani SQLite-dan PostgreSQL-ga o'tkazishimiz kerak bo'ladi).

---

## 💡 Maslahat
Bot orqali birinchi 100 000 so'm pul ishlaganingizdan so'ng, oyiga $5-10 bo'ladigan **VPS** (masalan, Hetzner yoki DigitalOcean) sotib olishni maslahat beraman. Bu botingizni juda tez va stabil qiladi.

**Savollaringiz bo'lsa, so'rashingiz mumkin!**
