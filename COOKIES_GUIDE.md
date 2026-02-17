# Cookies yordamida blokdan chiqish qo'llanmasi 🍪

Agar bot hali ham YouTube-dan video/musiqa yuklashda "Sign in to confirm you're not a bot" xatosini bersa, siz o'z brauzeringizdagi "cookie" ma'lumotlarini botga berishingiz kerak bo'ladi.

## 1-qadam: Cookie-ni eksport qilish

1. Brauzeringizga (Chrome, Edge yoki Firefox) **"Get Cookies.txt LOCALLY"** yoki shunga o'xshash extension o'rnating.
2. [YouTube.com](https://www.youtube.com) sahifasiga kiring (akkauntingizga kirgan bo'lishingiz tavsiya etiladi).
3. Extension-ni bosing va **"Export to cookies.txt"** tugmasini bosing.
4. Faylni kompyuteringizga saqlang.

## 2-qadam: Botga yuklash

Ushbu `cookies.txt` faylini botning asosiy papkasiga (qayerda `bot.py` turgan bo'lsa) joylashtiring.

## 3-qadam: GitHub-ga push qilish

Faylni GitHub-ga yuboring:

```bash
git add cookies.txt
git commit -m "Add authentication cookies"
git push
```

Render kodingizni yangilaganidan so'ng, bot bloklarni osongina chetlab o'ta oladi.

---
**DIQQAT!** `cookies.txt` faylida sizning shaxsiy ma'lumotlaringiz bo'lishi mumkin. Uni faqat o'zingiz ishongan serverlarga (Render/GitHub Private) joylang.
