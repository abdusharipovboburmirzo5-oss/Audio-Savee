# 🚀 Botni Tekin Serverga Qo'yish (Deployment Guide)

Do'stim, mablag'ingiz bo'lmasa ham botni ishga tushirib, pul ishlashni boshlashingiz mumkin. Quyida eng yaxshi 3 ta tekin variantni tayyorladim.

## 1-Variant: Koyeb (Eng osoni)
Koyeb sizga Docker orqali botni bepull ishlatish imkonini beradi.

1. [Koyeb.com](https://www.koyeb.com/) saytidan ro'yxatdan o'ting.
2. **"Create Service"** tugmasini bosing.
3. **GitHub**-ni ulang va bot kodingiz turgan repozitoriyani tanlang.
4. **Build Strategy**: Docker-ni tanlang (u bizni `Dockerfile`-ni avtomatik taniydi).
5. **Environment Variables** bo'limida `BOT_TOKEN` va boshqa kerakli kalitlarni kiriting.
6. **Deploy** tugmasini bosing.

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

## 💾 Ma'lumotlar Bazasi (Persistence)

Tekin serverlar odatda fayllarni o'chirib yuboradi. Foydalanuvchilar balansini yo'qotmaslik uchun:
1. [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-free-tier) - 512MB tekin baza beradi.
2. [Aiven.io](https://aiven.io/postgresql) - Tekin PostgreSQL (bazani SQLite-dan PostgreSQL-ga o'tkazishimiz kerak bo'ladi).

---

## 💡 Maslahat
Bot orqali birinchi 100 000 so'm pul ishlaganingizdan so'ng, oyiga $5-10 bo'ladigan **VPS** (masalan, Hetzner yoki DigitalOcean) sotib olishni maslahat beraman. Bu botingizni juda tez va stabil qiladi.

**Savollaringiz bo'lsa, so'rashingiz mumkin!**
