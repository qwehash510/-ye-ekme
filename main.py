import logging
import asyncio
import random
from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsRecent
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError

# --- AYARLAR ---
API_ID = 33188452
API_HASH = 'ac4afbd122081956a173b16590c02609'
BOT_TOKEN = '8520192303:AAGxF3gRP8LG6fjusT55dpJK0E3eNa3Qd48'   

BOT_NAME = "! Jun. OTOMATİK ÇEKİCİ"
OWNERS = {8571066107}   # <-- BURAYA KENDİ TELEGRAM ID'Nİ YAZ

client = TelegramClient('jun_auto_puller', API_ID, API_HASH)
client.flood_sleep_threshold = 0

logging.basicConfig(level=logging.ERROR)
pull_active = False

@client.on(events.NewMessage(pattern='/cek', chats=None))
async def auto_member_puller(event):
    global pull_active
    if event.sender_id not in OWNERS or not event.is_private or pull_active:
        return

    pull_active = True

    try:
        cmd = event.message.text.split()
        if len(cmd) < 3:
            await event.respond("❌ **Kullanım:** `/cek @target_grup @senin_grup 5000`")
            pull_active = False
            return

        target_username = cmd[1]
        your_group_username = cmd[2]
        limit = int(cmd[3]) if len(cmd) > 3 else 10000

        target_chat = await client.get_entity(target_username)
        your_chat = await client.get_entity(your_group_username)

        await event.respond(f"🔥 **{BOT_NAME} KURALSIZ OTOMATİK MOD AKTİF!**\nTarget: **{target_chat.title}**\nSenin Grup: **{your_chat.title}**\nÜyeler taranıyor ve zorla çekiliyor...")

        # === TARGET GRUPTAN GERÇEK ÜYELERİ TARASIN ===
        members = set()
        try:
            offset = 0
            while len(members) < limit:
                participants = await client(GetParticipantsRequest(
                    channel=target_chat,
                    filter=ChannelParticipantsRecent(),
                    offset=offset,
                    limit=200,
                    hash=0
                ))
                if not participants.users:
                    break
                for p in participants.users:
                    if not getattr(p, 'bot', False) and not getattr(p, 'is_self', False):
                        members.add(p.id)
                offset += len(participants.users)
                await asyncio.sleep(0.01)  # Tarama hızı
        except Exception as e:
            await event.respond(f"⚠ Tarama hatası: {e}\nDevam ediyorum...")

        member_list = list(members)
        await event.respond(f"🚀 **Tarama bitti!** {len(member_list)} gerçek üye bulundu.\nŞimdi **zorla** senin grubuna çekiyorum... Delay sıfır, kuralsız!")

        # === SENİN GRUBUNA ZORLA ÇEK (InviteToChannelRequest) ===
        added = 0
        for uid in member_list:
            try:
                await client(InviteToChannelRequest(your_chat, [uid]))
                added += 1
                if added % 20 == 0:
                    await event.respond(f"🔄 **Çekme devam ediyor...** Eklenen: **{added}** / {len(member_list)}")
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except (UserPrivacyRestrictedError, PeerFloodError):
                pass  # Gizli hesap veya flood, atla
            except Exception:
                pass  # Her hatada devam et, durma

        await event.respond(f"✅ **{BOT_NAME} OTOMATİK ÇEKME TAMAMLANDI!**\nSenin Grup: **{your_chat.title}**\nEklenen: **{added}** üye\nKuralsız mod bitti 🔥")
    except Exception as e:
        await event.respond(f"❌ Genel hata: {e}")
    finally:
        pull_active = False


@client.on(events.NewMessage(pattern='/start', chats=None))
async def start(event):
    if event.sender_id in OWNERS and event.is_private:
        await event.respond(f"✅ **{BOT_NAME} Otomatik Üye Çekici**\n\nKullanım: `/cek @target_grup @senin_grup 5000`\nBot target gruba girip herkesi tarayacak ve senin grubuna zorla çekecek.")


async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("🚀 Kuralsız Otomatik Üye Çekici Botu çalışıyor...")
    await client.run_until_disconnected()

asyncio.run(main())
