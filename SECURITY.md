# 🔐 Xavfsizlik Bo'yicha Qo'llanma (Security Guide)

## ⚠️ Muhim Qoidalar

### 1. Tokenlarni HECH QACHON ommaviy qilmang!
- `.env` faylini **hech qachon** GitHub-ga push qilmang
- BOT_TOKEN va ADMIN_CHAT_ID sir bo'lishi kerak
- `.gitignore` da `.env` fayli yozilgan bo'lishi shart

### 2. Agar token oshkor bo'lsa
1. **Darhol** @BotFather ga boring
2. `/revoke` buyrug'i bilan **eski tokenni bekor qiling**
3. Yangi token oling va `.env` faylini yangilang

### 3. Admin Xavfsizligi
- `ADMIN_IDS` muhit o'zgaruvchisi orqali adminlarni belgilang
- Bir nechta admin qo'shish: `ADMIN_IDS=123456,789012`
- Broadcast uchun 1 soatlik cooldown mavjud

### 4. Rate Limiting
Bot spam va DDoS hujumlaridan himoyalangan:
- Har bir foydalanuvchi: daqiqada **10 ta xabar**
- Har bir foydalanuvchi: daqiqada **5 ta yuklab olish**
- Spammer foydalanuvchilar **60 soniyaga bloklanadilar**
- Adminlar rate limitdan **exempt** (ozod)

### 5. Ma'lumotlar Bazasi
- SQLite baza ishlatiladi (parametrlangan so'rovlar)
- SQL injection hujumlaridan himoyalangan
- Karta raqamlari bazada saqlanadi (minimal ma'lumot)

## 📋 Deploy Qilishdan Avvalgi Checklist

- [ ] `.env` faylida haqiqiy token bor
- [ ] `.gitignore` da `.env` yozilgan
- [ ] README/SETUP/DEPLOY da haqiqiy token yo'q
- [ ] `ADMIN_CHAT_ID` sozlangan
- [ ] Health check endpoint ishlayapti
- [ ] GitHub repoda sir yo'qligini tekshiring

## 🔍 Sir Skanerlash

Haqiqiy tokenlar qolmaganini tekshirish uchun:
```bash
grep -r "7637789321" .
grep -r "AAH" . --include="*.md"
```

Agar natija bo'lsa — shu fayllardan tokenni o'chiring!
