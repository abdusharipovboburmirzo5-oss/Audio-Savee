"""
Multi-language message templates for the bot
"""

MESSAGES = {
    'uz': {
        'start': """👋 Assalomu alaykum!

🤖 Men Instagram, TikTok va YouTube videolarini yuklab beruvchi botman!

📥 Quyidagilarni yuklab olishingiz mumkin:
• Instagram Reels & Stories
• TikTok Videolar (suv belgisiz)
• YouTube Videolar va Shorts
• Musiqa/Audio (to'liq formatda)
• Profil rasmlari

📎 Shunchaki linkni yuboring!

Yordam kerakmi? /help buyrug'ini yuboring.""",

        'help': """📖 Qo'llanma

🔗 Instagram linkini yuborish:
1. Instagram'da kerakli kontentni oching
2. "Ulashish" tugmasini bosing
3. "Linkni nusxalash" ni tanlang
4. Linkni menga yuboring

✅ Qo'llab-quvvatlanadigan formatlar:
• Reels: /reel/xxxxx
• Post: /p/xxxxx
• IGTV: /tv/xxxxx
• Stories: /stories/xxxxx
• Profil: /username

⚙️ Sozlamalar: /settings
🌐 Til: /language""",

        'choose_format': '📥 Yuklab olish formatini tanlang:',
        'downloading': '⏳ Yuklab olinmoqda...',
        'processing': '🔄 Qayta ishlanmoqda...',
        'extracting_audio': '🎵 Musiqa ajratib olinmoqda...',
        'uploading': '📤 Yuborilmoqda...',
        'success': '✅ Tayyor!',
        'error': '❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.',
        'invalid_url': '❌ Noto\'g\'ri link. Iltimos, to\'g\'ri Instagram linkini yuboring.',
        'file_too_large': '❌ Fayl hajmi juda katta (max 50MB). Telegram cheklovi.',
        'private_account': '❌ Bu shaxsiy akkaunt. Faqat ochiq kontentlarni yuklab olish mumkin.',
        'not_found': '❌ Kontent topilmadi yoki o\'chirilgan.',
        'choose_language': '🌐 Tilni tanlang:',
        'language_changed': '✅ Til o\'zgartirildi!',
        'search_searching': '🔍 Qidirilmoqda: <b>{query}</b>...',
        'search_results': '🎵 <b>{title}</b> uchun variantni tanlang:',
        'search_results_list': '🔍 <b>"{query}"</b> bo\'yicha topilgan natijalar:',
        'select_song': '👇 Kerakli musiqani tanlang:',
        'music_not_found': '❌ Musiqa topilmadi.',
        'settings': '⚙️ <b>Sozlamalar</b>\n\n🔄 Avtomatik musiqa: {auto_audio}',
        'on': '✅ YOQILGAN',
        'off': '❌ O\'CHIRILGAN',
        'auto_audio_changed': '🔄 Avtomatik musiqa rejimi o\'zgartirildi!',
        'my_stats': '📊 <b>Sizning statistikangiz:</b>\n\n📥 Jami yuklamalar: {total}\n🎵 Musiqa: {music}\n📹 Video: {video}\n📸 Foto: {photo}',
        'recent_downloads': '🕒 <b>Oxirgi yuklamalaringiz:</b>\n\n{list}',
        'top_music': '🔥 <b>Eng ko\'p yuklangan musiqalar:</b>\n\n{list}',
        'admin_stats': '📊 <b>Bot Statistikasi:</b>\n\n👥 Jami foydalanuvchilar: {total_users}\n📥 Jami yuklamalar: {total_downloads}\n📈 Bugungi yuklamalar: {today_downloads}',
        'broadcast_prompt': '📢 Reklama yoki xabar matnini yuboring (yoki bekor qilish uchun /cancel deb yozing):',
        'broadcast_success': '✅ Xabar {count} ta foydalanuvchiga muvaffaqiyatli yuborildi.',
        'favorites_list': '⭐ <b>Sizning saralangan musiqalaringiz:</b>\n\n{list}',
        'favorite_added': '✅ Musiqa saralanganlarga qo\'shildi!',
        'favorite_removed': '❌ Musiqa saralanganlardan olib tashlandi.',
        'no_favorites': '📭 Sizda hali saralangan musiqalar yo\'q.',
        'profile': '👤 <b>Profil</b>\n\n🆔 ID: <code>{user_id}</code>\n👤 Ism: {first_name}\n🌐 Til: {lang}',
        'sub_required': '❌ <b>Botdan foydalanish uchun kanalimizga obuna bo\'lishingiz shart!</b>\n\nPastdagi tugmani bosib obuna bo\'ling va "Tekshirish" tugmasini bosing.',
        'sub_thank_you': '✅ Rahmat! Endi botdan to\'liq foydalanishingiz mumkin.',
        'referral_text': '🎁 <b>Referal tizimi</b>\n\nDo\'stlaringizni botga taklif qiling va har bir do\'stingiz uchun <b>500 so\'m</b> mukofot oling!\n\nSizning referal havolaingiz:\n<code>{link}</code>\n\n📊 Taklif qilingan do\'stlar: {count} ta',
        'wallet_text': '💰 <b>Sizning hamyoningiz</b>\n\n💵 <b>Balansingiz:</b> {balance} so\'m\n👥 <b>Takliflaringiz:</b> {count} ta\n\n💎 Har bir taklif uchun <b>500 so\'m</b> beriladi.',
        'withdraw_prompt': '💳 <b>Pulni yechish</b>\n\nPul yechish uchun karta raqamingizni yuboring.\n\n⚠️ <i>Misol: 8600123456789012 (Humo yoki Uzcard)</i>',
        'withdraw_min': '❌ <b>Xatolik!</b>\n\nMinimal yechish miqdori: <b>{min_amount} so\'m</b>.\nSizning balansingiz: {balance} so\'m.',
        'withdraw_success_msg': '✅ <b>Ajoyib!</b>\n\nSizning {amount} so\'m yechish so\'rovingiz adminga yuborildi. Tez orada ko\'rib chiqiladi.',
        'share_bot': '🤖 Bu bot orqali Instagram va YouTube\'dan videolarni juda tez yuklab olishingiz mumkin!',
        'tools_prompt': '🛠 <b>Asboblar:</b> Media bilan nima qilmoqchisiz?',
        'tool_trim_prompt': '✂️ <b>Qirqish:</b> Iltimos, boshlanish va tugash vaqtini yuboring.\n\nMisol: <code>00:10 00:30</code> (10-soniyadan 30-soniyagacha)',
        'tool_speed_prompt': '⚡ <b>Tezlikni tanlang:</b>',
        'tool_processing': '🔄 Qayta ishlanmoqda...',
    },
    
    'ru': {
        'start': """👋 Здравствуйте!

🤖 Я бот для скачивания контента из Instagram!

📥 Вы можете скачать:
• Instagram Reels
• Посты (фото и видео)
• Stories
• IGTV видео
• Музыку/Аудио
• Фото профиля

📎 Просто отправьте ссылку на Instagram!

Нужна помощь? Отправьте /help""",

        'help': """📖 Руководство

🔗 Как отправить ссылку Instagram:
1. Откройте нужный контент в Instagram
2. Нажмите кнопку "Поделиться"
3. Выберите "Копировать ссылку"
4. Отправьте ссылку мне

✅ Поддерживаемые форматы:
• Reels: /reel/xxxxx
• Пост: /p/xxxxx
• IGTV: /tv/xxxxx
• Stories: /stories/xxxxx
• Профиль: /username

⚙️ Настройки: /settings
🌐 Язык: /language""",

        'choose_format': '📥 Выберите формат загрузки:',
        'downloading': '⏳ Загружается...',
        'processing': '🔄 Обрабатывается...',
        'extracting_audio': '🎵 Извлекается музыка...',
        'uploading': '📤 Отправляется...',
        'success': '✅ Готово!',
        'error': '❌ Произошла ошибка. Пожалуйста, попробуйте снова.',
        'invalid_url': '❌ Неверная ссылка. Пожалуйста, отправьте правильную ссылку Instagram.',
        'file_too_large': '❌ Файл слишком большой (макс 50MB). Ограничение Telegram.',
        'private_account': '❌ Это приватный аккаунт. Можно скачать только публичный контент.',
        'not_found': '❌ Контент не найден или удален.',
        'choose_language': '🌐 Выберите язык:',
        'language_changed': '✅ Язык изменен!',
        'search_searching': '🔍 Ищу: <b>{query}</b>...',
        'search_results': '🎵 Выберите вариант для <b>{title}</b>:',
        'search_results_list': '🔍 Результаты поиска для <b>"{query}"</b>:',
        'select_song': '👇 Выберите нужную песню:',
        'music_not_found': '❌ Музыка не найдена.',
        'settings': '⚙️ <b>Настройки</b>\n\n🔄 Авто-музыка: {auto_audio}',
        'on': '✅ ВКЛ',
        'off': '❌ ВЫКЛ',
        'auto_audio_changed': '🔄 Режим авто-музыки изменен!',
        'my_stats': '📊 <b>Ваша статистика:</b>\n\n📥 Всего загрузок: {total}\n🎵 Музыка: {music}\n📹 Видео: {video}\n📸 Фото: {photo}',
        'recent_downloads': '🕒 <b>Ваши последние загрузки:</b>\n\n{list}',
        'top_music': '🔥 <b>Самые популярные треки:</b>\n\n{list}',
        'admin_stats': '📊 <b>Статистика бота:</b>\n\n👥 Всего пользователей: {total_users}\n📥 Всего загрузок: {total_downloads}\n📈 Загрузок сегодня: {today_downloads}',
        'broadcast_prompt': '📢 Отправьте текст рекламы или сообщения (или /cancel для отмены):',
        'broadcast_success': '✅ Сообщение успешно отправлено {count} пользователям.',
        'favorites_list': '⭐ <b>Ваши избранные песни:</b>\n\n{list}',
        'favorite_added': '✅ Песня добавлена в избранное!',
        'favorite_removed': '❌ Песня удалена из избранного.',
        'no_favorites': '📭 У вас пока нет избранных песен.',
        'profile': '👤 <b>Профиль</b>\n\n🆔 ID: <code>{user_id}</code>\n👤 Имя: {first_name}\n🌐 Язык: {lang}',
        'tools_prompt': '🛠 <b>Инструменты:</b> Что вы хотите сделать с медиа?',
        'tool_trim_prompt': '✂️ <b>Обрезка:</b> Пожалуйста, отправьте время начала и окончания.\n\nПример: <code>00:10 00:30</code> (с 10 по 30 секунду)',
        'tool_speed_prompt': '⚡ <b>Выберите скорость:</b>',
        'tool_processing': '🔄 Обработка...',
    },
    
    'en': {
        'start': """👋 Hello!

🤖 I'm an Instagram content downloader bot!

📥 You can download:
• Instagram Reels
• Posts (photos and videos)
• Stories
• IGTV videos
• Music/Audio
• Profile pictures

📎 Just send me an Instagram link!

Need help? Send /help""",

        'help': """📖 Guide

🔗 How to send Instagram link:
1. Open the content in Instagram
2. Tap "Share" button
3. Select "Copy link"
4. Send the link to me

✅ Supported formats:
• Reels: /reel/xxxxx
• Post: /p/xxxxx
• IGTV: /tv/xxxxx
• Stories: /stories/xxxxx
• Profile: /username

⚙️ Settings: /settings
🌐 Language: /language""",

        'choose_format': '📥 Choose download format:',
        'downloading': '⏳ Downloading...',
        'processing': '🔄 Processing...',
        'extracting_audio': '🎵 Extracting audio...',
        'uploading': '📤 Uploading...',
        'success': '✅ Done!',
        'error': '❌ An error occurred. Please try again.',
        'invalid_url': '❌ Invalid link. Please send a valid Instagram link.',
        'file_too_large': '❌ File too large (max 50MB). Telegram limitation.',
        'private_account': '❌ This is a private account. Can only download public content.',
        'not_found': '❌ Content not found or deleted.',
        'choose_language': '🌐 Choose language:',
        'language_changed': '✅ Language changed!',
        'search_searching': '🔍 Searching for: <b>{query}</b>...',
        'search_results': '🎵 Choose a version for <b>{title}</b>:',
        'search_results_list': '🔍 Search results for <b>"{query}"</b>:',
        'select_song': '👇 Choose the desired song:',
        'music_not_found': '❌ Music not found.',
        'settings': '⚙️ <b>Settings</b>\n\n🔄 Auto-audio: {auto_audio}',
        'on': '✅ ON',
        'off': '❌ OFF',
        'auto_audio_changed': '🔄 Auto-audio mode changed!',
        'my_stats': '📊 <b>Your Statistics:</b>\n\n📥 Total downloads: {total}\n🎵 Music: {music}\n📹 Video: {video}\n📸 Photo: {photo}',
        'recent_downloads': '🕒 <b>Your Recent Downloads:</b>\n\n{list}',
        'top_music': '🔥 <b>Top Downloaded Music:</b>\n\n{list}',
        'admin_stats': '📊 <b>Bot Statistics:</b>\n\n👥 Total users: {total_users}\n📥 Total downloads: {total_downloads}\n📈 Today downloads: {today_downloads}',
        'broadcast_prompt': '📢 Send the message or ad text (or write /cancel to abort):',
        'broadcast_success': '✅ Message successfully sent to {count} users.',
        'favorites_list': '⭐ <b>Your favorite songs:</b>\n\n{list}',
        'favorite_added': '✅ Added to favorites!',
        'favorite_removed': '❌ Removed from favorites.',
        'no_favorites': '📭 You don\'t have any favorite songs yet.',
        'profile': '👤 <b>Profile</b>\n\n🆔 ID: <code>{user_id}</code>\n👤 Name: {first_name}\n🌐 Language: {lang}',
        'tools_prompt': '🛠 <b>Tools:</b> What do you want to do with the media?',
        'tool_trim_prompt': '✂️ <b>Trim:</b> Please send start and end time.\n\nExample: <code>00:10 00:30</code> (from 10th to 30th second)',
        'tool_speed_prompt': '⚡ <b>Select speed:</b>',
        'tool_processing': '🔄 Processing...',
    },
}

def get_message(lang: str, key: str) -> str:
    """Get message in specified language"""
    if lang not in MESSAGES:
        lang = 'uz'
    return MESSAGES[lang].get(key, MESSAGES['uz'].get(key, ''))
