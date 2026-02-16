"""
Inline keyboard layouts for the bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    """Keyboard layouts for different bot interactions"""
    
    @staticmethod
    def download_options(lang='uz'):
        """Main download options keyboard"""
        text = {
            'uz': {'video': '🎥 Video', 'audio': '🎵 Musiqa', 'photo': '📷 Foto'},
            'ru': {'video': '🎥 Видео', 'audio': '🎵 Музыка', 'photo': '📷 Фото'},
            'en': {'video': '🎥 Video', 'audio': '🎵 Audio', 'photo': '📷 Photo'},
        }
        t = text.get(lang, text['uz'])
        
        keyboard = [
            [
                InlineKeyboardButton(t['video'], callback_data='download_video'),
                InlineKeyboardButton(t['audio'], callback_data='download_audio'),
            ],
            [
                InlineKeyboardButton(t['photo'], callback_data='download_photo'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quality_options(content_type='video', lang='uz'):
        """Quality selection keyboard"""
        text = {
            'uz': {'hd': '🎬 HD Sifat', 'sd': '📱 SD Sifat', 'back': '⬅️ Orqaga'},
            'ru': {'hd': '🎬 HD Качество', 'sd': '📱 SD Качество', 'back': '⬅️ Назад'},
            'en': {'hd': '🎬 HD Quality', 'sd': '📱 SD Quality', 'back': '⬅️ Back'},
        }
        t = text.get(lang, text['uz'])
        
        keyboard = [
            [
                InlineKeyboardButton(t['hd'], callback_data=f'quality_{content_type}_hd'),
                InlineKeyboardButton(t['sd'], callback_data=f'quality_{content_type}_sd'),
            ],
            [
                InlineKeyboardButton(t['back'], callback_data='back_to_options'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def subscribe_keyboard(lang: str) -> InlineKeyboardMarkup:
        """Keyboard for force subscription"""
        from config import Config
        kb = [
            [InlineKeyboardButton("Obuna bo'lish 📢", url=Config.CHANNEL_URL)],
            [InlineKeyboardButton("Tekshirish ✅", callback_data="check_sub")]
        ]
        return InlineKeyboardMarkup(kb)

    @staticmethod
    def main_menu(lang: str) -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        text = {
            'uz': {'stats': '📊 Stat', 'history': '🕒 Tarix', 'wallet': '💰 Hamyon', 'set_lang': '🌐 Til', 'trending': '🔥 Trendlar'},
            'ru': {'stats': '📊 Стат', 'history': '🕒 История', 'wallet': '💰 Кошелек', 'set_lang': '🌐 Язык', 'trending': '🔥 Тренды'},
            'en': {'stats': '📊 Stats', 'history': '🕒 History', 'wallet': '💰 Wallet', 'set_lang': '🌐 Language', 'trending': '🔥 Trending'},
        }
        t = text.get(lang, text['uz'])
        
        keyboard = [
            [
                InlineKeyboardButton(t['stats'], callback_data="my_stats"),
                InlineKeyboardButton(t['history'], callback_data="recent")
            ],
            [
                InlineKeyboardButton(t['trending'], callback_data="trending"),
                InlineKeyboardButton(t['wallet'], callback_data="wallet")
            ],
            [
                InlineKeyboardButton("💎 Premium", callback_data="premium_menu"),
                InlineKeyboardButton(t['set_lang'], callback_data="set_lang")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def premium_menu(lang: str) -> InlineKeyboardMarkup:
        """Keyboard for premium features and upgrade"""
        # Check if premium status via DB would be better but this is static keyboard
        kb = [
            [InlineKeyboardButton("💳 1 oylik Premium (15 000 so'm)", callback_data="buy_prem_30")],
            [InlineKeyboardButton("💳 3 oylik Premium (40 000 so'm)", callback_data="buy_prem_90")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(kb)
    
    @staticmethod
    def language_selection():
        """Language selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton('🇺🇿 O\'zbekcha', callback_data='lang_uz'),
                InlineKeyboardButton('🇷🇺 Русский', callback_data='lang_ru'),
            ],
            [
                InlineKeyboardButton('🇬🇧 English', callback_data='lang_en'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def music_search_results(results, lang='uz'):
        """Keyboard for showing top 10 music search results"""
        keyboard = []
        for res in results:
            # Shorten title if too long
            title = res['title']
            if len(title) > 40:
                title = title[:37] + "..."
            
            # Format duration (seconds to min:sec)
            duration = ""
            if res.get('duration'):
                mins = int(res['duration'] // 60)
                secs = int(res['duration'] % 60)
                duration = f" [{mins}:{secs:02d}]"
            
            keyboard.append([InlineKeyboardButton(f"🎵 {title}{duration}", callback_data=f"sl_song_{res['id']}")])
        
        # Add cancel button
        cancel_text = {'uz': '❌ Bekor qilish', 'ru': '❌ Отмена', 'en': '❌ Cancel'}
        keyboard.append([InlineKeyboardButton(cancel_text.get(lang, cancel_text['uz']), callback_data='cancel')])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def music_versions(song_id, lang='uz', available_versions=None):
        """Music version selection keyboard - only shows available versions"""
        if available_versions is None:
            available_versions = ['original', '8d', 'slowed', 'concert', 'bass', 'nightcore']
            
        text = {
            'uz': {'8d': '🎧 8D Versiya', 'slowed': '🐌 Slowed', 'concert': '🎸 Concert', 'original': '🎵 Original', 'bass': '🔊 Bass', 'nightcore': '⚡ Nightcore'},
            'ru': {'8d': '🎧 8D Версия', 'slowed': '🐌 Slowed', 'concert': '🎸 Концерт', 'original': '🎵 Оригинал', 'bass': '🔊 Басс', 'nightcore': '⚡ Nightcore'},
            'en': {'8d': '🎧 8D Version', 'slowed': '🐌 Slowed', 'concert': '🎸 Concert', 'original': '🎵 Original', 'bass': '🔊 Bass', 'nightcore': '⚡ Nightcore'},
        }
        t = text.get(lang, text['uz'])
        
        all_buttons = []
        for v in ['original', '8d', 'slowed', 'concert', 'bass', 'nightcore']:
            if v in available_versions:
                all_buttons.append(InlineKeyboardButton(t.get(v, v), callback_data=f'msv_{v}_{song_id}'))
        
        # Grid layout (2 buttons per row)
        keyboard = []
        for i in range(0, len(all_buttons), 2):
            keyboard.append(all_buttons[i:i+2])
            
        keyboard.append([
            InlineKeyboardButton(t.get('back', '⬅️ Orqaga'), callback_data='cancel'),
            InlineKeyboardButton(t.get('close', '❌ Yopish'), callback_data='cancel')
        ])
        
        # Add 'Add to Favorites' button if a song_id is provided
        fav_text = {'uz': '⭐ Saralanganlarga qo\'shish', 'ru': '⭐ Добавить в избранное', 'en': '⭐ Add to Favorites'}
        keyboard.append([InlineKeyboardButton(fav_text.get(lang, fav_text['uz']), callback_data=f'add_fav_{song_id}')])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings(auto_audio_status, lang='uz'):
        """Settings keyboard with auto-audio toggle"""
        text = {
            'uz': {'auto_audio': '🔄 Avtomatik musiqa: ', 'back': '⬅️ Orqaga', 'on': '✅ YOQILGAN', 'off': '❌ O\'CHIRILGAN'},
            'ru': {'auto_audio': '🔄 Авто-музыка: ', 'back': '⬅️ Назад', 'on': '✅ ВКЛ', 'off': '❌ ВЫКЛ'},
            'en': {'auto_audio': '🔄 Auto-audio: ', 'back': '⬅️ Back', 'on': '✅ ON', 'off': '❌ OFF'},
        }
        t = text.get(lang, text['uz'])
        
        status_text = t['on'] if auto_audio_status else t['off']
        
        keyboard = [
            [
                InlineKeyboardButton(f"{t['auto_audio']}{status_text}", callback_data='toggle_auto_audio'),
            ],
            [
                InlineKeyboardButton(t['back'], callback_data='cancel'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancel_button(lang='uz'):
        """Cancel button"""
        text = {
            'uz': '❌ Bekor qilish',
            'ru': '❌ Отмена',
            'en': '❌ Cancel',
        }
        t = text.get(lang, text['uz'])
        
        keyboard = [[InlineKeyboardButton(t, callback_data='cancel')]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def wallet(lang: str) -> InlineKeyboardMarkup:
        """Keyboard for wallet section"""
        kb = [
            [InlineKeyboardButton("🔗 Taklif havolasi", callback_data="referral")],
            [InlineKeyboardButton("💳 Pulni yechish", callback_data="withdraw_start")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(kb)

    @staticmethod
    def withdraw_cancel(lang: str) -> InlineKeyboardMarkup:
        """Keyboard to cancel withdrawal"""
        kb = [[InlineKeyboardButton("❌ Bekor qilish", callback_data="wallet")]]
        return InlineKeyboardMarkup(kb)

    @staticmethod
    def back_button(lang='uz'):
        """Back button"""
        text = {
            'uz': '⬅️ Orqaga',
            'ru': '⬅️ Назад',
            'en': '⬅️ Back',
        }
        t = text.get(lang, text['uz'])
        
        keyboard = [[InlineKeyboardButton(t, callback_data='back_to_main')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def tools_menu(filepath: str, lang='uz'):
        """Menu for media processing tools"""
        text = {
            'uz': {
                'trim': '✂️ Qirqish', 
                'voice': '🎤 Ovozli xabar', 
                'mute': '🔇 Ovozni o\'chirish',
                'speed': '⚡ Tezlik',
                'lyrics': '📝 Matn',
                'lyrics_card': '🖼 Matnli rasm',
                'translate': '🌐 Tarjima',
                'effects': '🪄 Effektlar',
                'back': '⬅️ Bekor qilish'
            },
            'ru': {
                'trim': '✂️ Обрезать', 
                'voice': '🎤 Голос', 
                'mute': '🔇 Без звука',
                'speed': '⚡ Скорость',
                'lyrics': '📝 Текст',
                'lyrics_card': '🖼 Текст-карта',
                'translate': '🌐 Перевод',
                'effects': '🪄 Эффекты',
                'back': '⬅️ Отмена'
            },
            'en': {
                'trim': '✂️ Trim', 
                'voice': '🎤 Voice', 
                'mute': '🔇 Mute',
                'speed': '⚡ Speed',
                'lyrics': '📝 Lyrics',
                'lyrics_card': '🖼 Lyrics Card',
                'translate': '🌐 Translate',
                'effects': '🪄 Effects',
                'summary': '📊 YouTube Summary',
                'back': '⬅️ Cancel'
            },
        }
        t = text.get(lang, text['uz'])
        
        # Determine if it's video or audio based on extension
        is_video = filepath.lower().endswith(('.mp4', '.mkv', '.webm', '.mov'))
        
        keyboard = []
        # First row: Trim and Voice (Voice for audio mostly, but can be for video too)
        keyboard.append([
            InlineKeyboardButton(t['trim'], callback_data=f"tool_trim_init"),
            InlineKeyboardButton(t['voice'], callback_data=f"tool_voice_conv")
        ])
        
        if is_video:
            # Second row for video tools
            keyboard.append([
                InlineKeyboardButton(t['mute'], callback_data=f"tool_mute_vid"),
                InlineKeyboardButton(t['speed'], callback_data=f"tool_speed_init")
            ])
            # Add Summary for YouTube
            if 'youtube.com' in filepath or 'youtu.be' in filepath or 'youtube' in filepath.lower():
                keyboard.append([InlineKeyboardButton(t['summary'], callback_data="tool_summary")])
        else:
            # Lyrics for audio
            keyboard.append([
                InlineKeyboardButton(t['lyrics'], callback_data=f"tool_lyrics_get"),
                InlineKeyboardButton(t['lyrics_card'], callback_data=f"tool_lyrics_card")
            ])
            keyboard.append([
                InlineKeyboardButton(t['translate'], callback_data=f"tool_translate"),
                InlineKeyboardButton(t['effects'], callback_data=f"tool_effects_init")
            ])
            
        keyboard.append([InlineKeyboardButton(t['back'], callback_data='cancel')])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def audio_effects(lang='uz'):
        """Audio effects selection keyboard"""
        text = {
            'uz': {'bass': '🔊 Bass Boost', '8d': '🎧 8D Versiya', 'slowed': '🌙 Slowed', 'back': '⬅️ Orqaga'},
            'ru': {'bass': '🔊 Bass Boost', '8d': '🎧 8D Версия', 'slowed': '🌙 Slowed', 'back': '⬅️ Назад'},
            'en': {'bass': '🔊 Bass Boost', '8d': '🎧 8D Version', 'slowed': '🌙 Slowed', 'back': '⬅️ Back'},
        }
        t = text.get(lang, text['uz'])
        
        keyboard = [
            [
                InlineKeyboardButton(t['bass'], callback_data="tool_effect_bass_boost"),
                InlineKeyboardButton(t['8d'], callback_data="tool_effect_8d"),
            ],
            [
                InlineKeyboardButton(t['slowed'], callback_data="tool_effect_slowed_reverb"),
            ],
            [
                InlineKeyboardButton(t['back'], callback_data="tool_back_to_tools")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def speed_options(lang='uz'):
        """Speed selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("0.5x", callback_data="tool_speed_set_0.5"),
                InlineKeyboardButton("1.5x", callback_data="tool_speed_set_1.5"),
            ],
            [
                InlineKeyboardButton("2.0x", callback_data="tool_speed_set_2.0"),
            ],
            [
                InlineKeyboardButton("⬅️ Orqaga", callback_data="tool_back_to_tools")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
