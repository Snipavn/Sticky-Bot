# Tải package pip install discord dotenv
# Chúng mày nhớ ghi credit vào
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Danh sách ID người được phép dùng lệnh (admin custom)
ADMIN_IDS = [882844895902040104]  # Thay bằng ID thật của bạn

# Lưu sticky theo kênh: {channel_id: {"content": str, "message_id": int}}
sticky_messages = {}

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} đã sẵn sàng.")
    sticky_loop.start()

def is_custom_admin():
    async def predicate(ctx):
        return ctx.author.id in ADMIN_IDS
    return commands.check(predicate)

@bot.command(name="setsticky")
@is_custom_admin()
async def set_sticky(ctx, *, message: str):
    """Đặt sticky message (chỉ user trong ADMIN_IDS mới dùng được)"""
    channel = ctx.channel

    if channel.id in sticky_messages:
        try:
            old_msg = await channel.fetch_message(sticky_messages[channel.id]["message_id"])
            await old_msg.delete()
        except:
            pass

    sent_msg = await channel.send(f"📌 {message}")
    sticky_messages[channel.id] = {
        "content": message,
        "message_id": sent_msg.id
    }

    await ctx.send("✅ Sticky message đã được đặt!")

@bot.command(name="clearsticky")
@is_custom_admin()
async def clear_sticky(ctx):
    """Xóa sticky message"""
    channel = ctx.channel

    if channel.id in sticky_messages:
        try:
            msg = await channel.fetch_message(sticky_messages[channel.id]["message_id"])
            await msg.delete()
        except:
            pass
        del sticky_messages[channel.id]
        await ctx.send("✅ Đã xoá sticky message.")
    else:
        await ctx.send("⚠️ Không có sticky message trong kênh này.")

@tasks.loop(seconds=75s)
async def sticky_loop():
    """Tự động gửi sticky mỗi 75s giây"""
    for channel_id, data in sticky_messages.items():
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                try:
                    old_msg = await channel.fetch_message(data["message_id"])
                    await old_msg.delete()
                except:
                    pass
                new_msg = await channel.send(f"📌 {data['content']}")
                sticky_messages[channel_id]["message_id"] = new_msg.id
            except Exception as e:
                print(f"Lỗi khi gửi sticky ở kênh {channel_id}: {e}")
bot.run(TOKEN)
