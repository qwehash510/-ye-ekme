import os
import re
import requests
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest

# --- AYARLAR ---
API_ID = int(os.environ.get("33188452"))
API_HASH = os.environ.get("ac4afbd122081956a173b16590c02609"))
BOT_TOKEN = os.environ.get("8768489504:AAF8LhLWKztJusq8CjrpQ2kk3dKW7mGr33U"))

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
    return r["data"]["play"], r["data"]["music"]

# Kullanıcı sadece bu gruba üye olursa kullanabilir
ALLOWED_GROUP = "vxtikan"  # Grup kullanıcı adı

# Kullanıcının gruba katılıp katılmadığını kontrol
async def check_membership(user_id):
    try:
        await client(GetParticipantRequest(channel=ALLOWED_GROUP, user_id=user_id))
        return True
    except:
        return False

# --- START MENÜSÜ ---
@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.out:
        return

    await event.reply(
        f"⚠️ Bu botu kullanmak için **https://t.me/{ALLOWED_GROUP}** grubuna katılmalısınız.",
        buttons=[
            [Button.url("Gruba Katıl", f"https://t.me/{ALLOWED_GROUP}")],
            [Button.inline("Katıldım ✅", data="check_join")]
        ]
    )

# --- KATILDI BUTONU ---
@client.on(events.CallbackQuery(data="check_join"))
async def check_join(event):
    user_id = event.sender_id
    if await check_membership(user_id):
        await event.edit(
            "✅ Onaylandı! Artık botu kullanabilirsiniz.\n\n"
            "📌 Kullanımı:\n"
            "1. TikTok linkini kopyala\n"
            "2. Bana gönder\n"
            "3. Video ve ses dosyalarını al\n\n"
            "🛠 Developer: @primalamazsin"
        )
    else:
        await event.answer("❌ Önce gruba katılmalısınız!", alert=True)

# --- TikTok mesajları ---
@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return

    user_id = event.sender_id
    if not await check_membership(user_id):
        return  # Üye değilse hiçbir şey yapma

    text = event.raw_text
    if is_tiktok(text):
        await event.reply("İndiriliyor... ⏳")
        video, music = download_tiktok(text)
        if not video:
            await event.reply("❌ Hata oluştu")
            return
        await client.send_file(event.chat_id, video, caption="🎥 Video")
        await client.send_file(event.chat_id, music, caption="🎧 Ses (MP3)")
    else:
        if not text.startswith("/start"):
            await event.reply("📎 Bana TikTok linki gönder")

client.run_until_disconnected()
