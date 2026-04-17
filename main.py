import discord
from discord.ext import commands
import os
import random
import asyncio
import yt_dlp

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# DATABASE (RAM)
# =========================
coins = {}
xp = {}
level = {}
warns = {}

# =========================
# HELP FUNCTION
# =========================
@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")

# =========================
# ECONOMY
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
# LEVEL SYSTEM
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
        await message.channel.send(f"📈 {message.author.mention} ist Level {lvl+1}!")

    await bot.process_commands(message)

# =========================
# WARN SYSTEM
# =========================
@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="Kein Grund"):
    user = member.id
    warns[user] = warns.get(user, 0) + 1

    await ctx.send(f"⚠️ Warn {member.mention} ({warns[user]}/3)")

    if warns[user] >= 3:
        await member.kick(reason="3 Warns")
        await ctx.send("👢 automatisch gekickt!")

# =========================
# KICK
# =========================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Kein Grund"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} gekickt")

# =========================
# BAN
# =========================
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Kein Grund"):
    await member.ban(reason=reason)
    await ctx.send(f"⛔ {member} gebannt")

# =========================
# ROLE
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"🎭 Rolle gegeben: {role.name}")

# =========================
# AI CHAT
# =========================
@bot.command()
async def ai(ctx, *, msg):
    await ctx.send(random.choice(["Ja 🤖", "Nein ❌", "Vielleicht 🤔", "Okay 👍"]))

# =========================
# TICKET SYSTEM
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

    await channel.send("🎟 Ticket erstellt!")
    await ctx.send("✅ Ticket erstellt!")

@bot.command()
async def close(ctx):
    if "ticket" in ctx.channel.name:
        await ctx.send("🔒 Ticket wird geschlossen...")
        await asyncio.sleep(2)
        await ctx.channel.delete()

# =========================
# 🎵 MUSIC SYSTEM (FIXED)
# =========================

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("🔊 Joined Voice")
    else:
        await ctx.send("❌ Du bist nicht im Voice")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left Voice")

@bot.command()
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("❌ Geh zuerst in Voice")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    voice = ctx.voice_client

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]

    source = await discord.FFmpegOpusAudio.from_probe(audio_url)

    voice.play(source)
    await ctx.send(f"🎵 Playing: {info['title']}")

# =========================
# START BOT
# =========================
bot.run(os.getenv("TOKEN"))
