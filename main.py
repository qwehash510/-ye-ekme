import os
import requests
from telethon import TelegramClient, events, Button

# ---------------- AYARLAR ----------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Grup reklamı
GROUP_LINK = "https://t.me/vxtikan"

# ---------------- TELETHON CLIENT ----------------
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ---------------- YARDIMCI FONKSİYONLAR ----------------
def is_tiktok(url):
    return "tiktok.com" in url

def download_tiktok(url):
    """TikTok videolarını ve müziklerini indirir"""
    try:
        api = f"https://tikwm.com/api/?url={url}"
        r = requests.get(api).json()
        if r["code"] != 0:
            return None, None
        return r["data"]["play"], r["data"]["music"]
    except:
        return None, None

def usage_text():
    """Kullanım rehberi metni"""
    return (
        "✨ *Merhaba Sevgili Kullanıcı!* ✨\n\n"
        "🎬 Bu bot sayesinde TikTok videolarını ve MP3 seslerini kolayca indirebilirsiniz.\n\n"
        f"📣 Eğer grubumuza katılırsanız çok seviniriz: [Katılmak İçin Tıkla]({GROUP_LINK})\n\n"
        "📌 *Kullanım Adımları:*\n"
        "1️⃣ TikTok linkini kopyala\n"
        "2️⃣ Bu linki bot’a gönder\n"
        "3️⃣ Bot size filigransız video ve MP3 sesini ayrı ayrı gönderecek\n\n"
        "🛠 Developer: @primalamazsin"
    )

# ---------------- /START ve /HELP MENÜSÜ ----------------
@client.on(events.NewMessage(pattern="/start|/help"))
async def start(event):
    if event.out:
        return
    await event.reply(
        usage_text(),
        buttons=[[Button.url("🌟 Gruba Katıl 🌟", GROUP_LINK)]]
    )

# ---------------- TIKTOK MESAJLARI ----------------
@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return

    text = event.raw_text
    if is_tiktok(text):
        msg = await event.reply("⏳ TikTok indiriliyor, lütfen bekleyin...")
        video, music = download_tiktok(text)
        if not video:
            await msg.edit("❌ Video indirilemedi, linki kontrol edin!")
            return
        await msg.edit("✅ Video ve ses hazır, gönderiliyor...")
        await client.send_file(event.chat_id, video, caption="🎥 TikTok Video")
        await client.send_file(event.chat_id, music, caption="🎧 TikTok MP3")
        await msg.delete()
    else:
        if not text.startswith("/start") and not text.startswith("/help"):
            await event.reply("📎 Lütfen geçerli bir TikTok linki gönderin!")

# ---------------- RUN ----------------
print("🤖 Bot çalışıyor...")
client.run_until_disconnected()
