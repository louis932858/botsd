import discord
from discord.ext import commands
import os
import random
import asyncio
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 📊 DATABASE
# =========================
coins = {}
xp = {}
level = {}
warns = {}
verification_codes = {}
music_queue = []

# =========================
# 🔐 VERIFICATION ROLE
# =========================
VERIFIED_ROLE_NAME = "👥⠀×⠀COMMUNITY⠀×⠀👥"

# =========================
# 🧾 LOG FUNCTION
# =========================
async def log(guild, msg):
    channel = discord.utils.get(guild.text_channels, name="logs")
    if channel:
        await channel.send(f"🧾 {msg}")

# =========================
# 🤖 ON READY
# =========================
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

# =========================
# 📈 XP + AUTO MOD
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = message.author.id

    # 🚫 Anti-Link
    if "http" in message.content:
        await message.delete()
        await message.channel.send("🚫 Keine Links erlaubt!")
        return

    # 📈 XP
    xp[user] = xp.get(user, 0) + 5
    lvl = level.get(user, 1)

    if xp[user] >= lvl * 100:
        level[user] = lvl + 1
        await message.channel.send(f"📈 {message.author.mention} ist Level {lvl+1}!")

    await bot.process_commands(message)

# =========================
# 💰 ECONOMY
# =========================
@bot.command()
async def daily(ctx):
    user = ctx.author.id
    coins[user] = coins.get(user, 0) + 100
    await ctx.send("💰 +100 Coins")

@bot.command()
async def balance(ctx):
    await ctx.send(f"💰 Coins: {coins.get(ctx.author.id, 0)}")

# =========================
# ⚠️ WARN SYSTEM
# =========================
@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="Kein Grund"):
    warns[member.id] = warns.get(member.id, 0) + 1

    await ctx.send(f"⚠️ Warn {member.mention} ({warns[member.id]}/3)")

    if warns[member.id] >= 3:
        await member.kick(reason="3 Warns")
        await ctx.send("👢 automatisch gekickt!")

# =========================
# 👢 KICK
# =========================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Kein Grund"):
    await member.kick(reason=reason)
    await ctx.send("👢 gekickt")

# =========================
# ⛔ BAN
# =========================
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Kein Grund"):
    await member.ban(reason=reason)
    await ctx.send("⛔ gebannt")

# =========================
# 🎭 ROLE GIVE
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"🎭 Rolle gegeben: {role.name}")

# =========================
# 🎟 TICKET SYSTEM
# =========================
@bot.command()
async def ticket(ctx):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await ctx.guild.create_text_channel(
        f"ticket-{ctx.author.name}",
        overwrites=overwrites
    )

    await channel.send("🎟 Support Ticket erstellt!")
    await ctx.send("✅ Ticket erstellt!")

@bot.command()
async def close(ctx):
    if "ticket" in ctx.channel.name:
        await ctx.send("🔒 Ticket wird geschlossen...")
        await asyncio.sleep(2)
        await ctx.channel.delete()

# =========================
# 🔐 VERIFICATION SYSTEM
# =========================
@bot.command()
async def verify(ctx):
    code = random.randint(1000, 9999)
    verification_codes[ctx.author.id] = code

    await ctx.author.send(f"🔐 Dein Code: {code}")
    await ctx.send("📩 Schau in deine DMs!")

@bot.command()
async def code(ctx, user_code: int):
    if ctx.author.id not in verification_codes:
        return await ctx.send("❌ Kein Code angefordert!")

    if verification_codes[ctx.author.id] == user_code:
        role = discord.utils.get(ctx.guild.roles, name=VERIFIED_ROLE_NAME)

        if role:
            await ctx.author.add_roles(role)
            await ctx.send("✅ Verifiziert!")
        else:
            await ctx.send("❌ Rolle nicht gefunden!")

        del verification_codes[ctx.author.id]
    else:
        await ctx.send("❌ Falscher Code!")

# =========================
# 🔊 MUSIC SYSTEM
# =========================
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("🔊 Beigetreten")
    else:
        await ctx.send("❌ Kein Voice")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Verlassen")

@bot.command()
async def play(ctx, url):
    if not ctx.author.voice:
        return await ctx.send("❌ Geh in Voice")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    voice = ctx.voice_client
    music_queue.append(url)

    if not voice.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    if len(music_queue) == 0:
        return

    url = music_queue.pop(0)

    ydl_opts = {"format": "bestaudio"}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio = info["url"]

    voice = ctx.voice_client
    source = await discord.FFmpegOpusAudio.from_probe(audio)

    def after(error):
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

    voice.play(source, after=after)
    await ctx.send(f"🎵 Now playing: {info['title']}")

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏭ Skip")

@bot.command()
async def stop(ctx):
    music_queue.clear()
    if ctx.voice_client:
        ctx.voice_client.stop()
    await ctx.send("⛔ Stop")

# =========================
# 🤖 AI
# =========================
@bot.command()
async def ai(ctx, *, msg):
    await ctx.send(random.choice(["Ja 🤖", "Nein ❌", "Vielleicht 🤔", "Okay 👍"]))

# =========================
# 🚀 START
# =========================
bot.run(os.getenv("TOKEN"))
