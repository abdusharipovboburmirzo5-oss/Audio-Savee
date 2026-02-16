
import asyncio
import os
from telegram import Bot
from config import Config

async def check():
    bot = Bot(Config.BOT_TOKEN)
    channel = Config.REQUIRED_CHANNEL
    print(f"Checking access to {channel}...")
    try:
        chat = await bot.get_chat(channel)
        print(f"✅ Chat found: {chat.title} (ID: {chat.id})")
        
        # Test get_chat_member
        try:
            me = await bot.get_me()
            status = await bot.get_chat_member(channel, me.id)
            print(f"✅ Bot status in channel: {status.status}")
            if status.status != 'administrator':
                print("⚠️ WARNING: Bot is NOT an administrator in the channel!")
        except Exception as e:
            print(f"❌ Error checking bot status in channel: {e}")
            
    except Exception as e:
        print(f"❌ Error accessing channel: {e}")

if __name__ == "__main__":
    asyncio.run(check())
