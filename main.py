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
# 📊 DATABASE (RAM)
# =========================
coins = {}
xp = {}
level = {}
warns = {}

# =========================
# 🧾 LOG SYSTEM
# =========================
async def log(guild, msg):
    channel = discord.utils.get(guild.text_channels, name="logs")
    if channel:
        await channel.send(f"🧾 {msg}")

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

    await channel.send("🎟 Ticket erstellt! Beschreibe dein Problem.")
    await ctx.send("✅ Ticket erstellt!")

@bot.command()
async def close(ctx):
    if "ticket" in ctx.channel.name:
        await ctx.send("🔒 Ticket wird geschlossen...")
        await asyncio.sleep(2)
        await ctx.channel.delete()

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
    user = ctx.author.id
    await ctx.send(f"💰 Coins: {coins.get(user, 0)}")

# =========================
# 📈 XP + LEVEL SYSTEM
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = message.author.id

    xp[user] = xp.get(user, 0) + 5
    lvl = level.get(user, 1)

    if xp[user] >= lvl * 100:
        level[user] = lvl + 1
        await message.channel.send(f"📈 {message.author.mention} ist Level {lvl + 1}!")

    await bot.process_commands(message)

# =========================
# ⚠️ WARN SYSTEM
# =========================
@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="Kein Grund"):
    user = member.id
    warns[user] = warns.get(user, 0) + 1

    await ctx.send(f"⚠️ Warn ({warns[user]}/3)")

    if warns[user] >= 3:
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
# 🎭 ROLE SYSTEM
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"🎭 Rolle gegeben: {role.name}")

# =========================
# 🤖 AI CHAT
# =========================
@bot.command()
async def ai(ctx, *, msg):
    await ctx.send(random.choice([
        "Ja 🤖",
        "Nein ❌",
        "Vielleicht 🤔",
        "Sehr wahrscheinlich ✅",
        "Interessant 😄"
    ]))

# =========================
# 🔊 MUSIC SYSTEM
# =========================
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("🔊 Beigetreten")
    else:
        await ctx.send("❌ Du bist nicht im Voice")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Verlassen")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ Geh zuerst in Voice")
            return

    voice = ctx.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    voice.play(discord.FFmpegPCMAudio(audio_url))
    await ctx.send(f"🎵 Playing: {info['title']}")

# =========================
# 🚀 START BOT (RAILWAY)
# =========================
bot.run(os.getenv("TOKEN"))
