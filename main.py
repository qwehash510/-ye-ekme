import re
import requests
from telethon import TelegramClient, events, Button

# --- AYARLAR ---
API_ID = 33188452
API_HASH = "ac4afbd122081956a173b16590c02609"
BOT_TOKEN = "8768489504:AAF8LhLWKztJusq8CjrpQ2kk3dKW7mGr33U"

client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# TikTok link kontrol
def is_tiktok(url):
    return "tiktok.com" in url

# Video ve MP3 indir
def download_tiktok(url):
    api = f"https://tikwm.com/api/?url={url}"
    r = requests.get(api).json()

    if r["code"] != 0:
        return None, None

    video = r["data"]["play"]
    music = r["data"]["music"]

    return video, music

# --- START MENÜSÜ ---
@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        "👋 Merhaba! Ben TikTok Video ve Ses İndirme Botuyum.\n\n"
        "📌 Kullanımı:\n"
        "1. TikTok linkini kopyala\n"
        "2. Bana gönder\n"
        "3. Video ve ses dosyalarını al\n\n"
        "🛠 Developer: @primalamazsin",
        buttons=[
            [Button.url("📱 TikTok Web", "https://www.tiktok.com")],
            [Button.inline("ℹ️ Yardım", data="help")]
        ]
    )

# Yardım butonu
@client.on(events.CallbackQuery(data="help"))
async def help_button(event):
    await event.edit(
        "📌 Kullanımı:\n"
        "TikTok linki gönder → Bot video ve ses dosyasını gönderecek.\n\n"
        "💡 Öneri: Uzun videolar için sabırlı olun."
    )

# TikTok linklerini yakalama
@client.on(events.NewMessage)
async def handler(event):
    text = event.raw_text

    if is_tiktok(text):
        await event.reply("İndiriliyor... ⏳")

        video, music = download_tiktok(text)

        if not video:
            await event.reply("Hata oluştu ❌")
            return

        # Video gönder
        await client.send_file(event.chat_id, video, caption="🎥 Video")

        # Ses gönder
        await client.send_file(event.chat_id, music, caption="🎧 Ses (MP3)")

    else:
        if not text.startswith("/start"):
            await event.reply("Bana TikTok linki gönder 📎")

client.run_until_disconnected()
