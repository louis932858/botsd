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

bot.remove_command("help")

# =========================
# DATABASE
# =========================
coins = {}
xp = {}
level = {}
warns = {}
verification_codes = {}
music_queue = []

# =========================
# ONDUTY SETTINGS
# =========================
ONDUTY_PASSWORD = "louis12"
ONDUTY_ROLES = ["★", "👑⠀×⠀CO OWNER⠀×⠀👑"]

# =========================
# START
# =========================
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

# =========================
# AUTO MOD
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 🚫 Links block
    if "http" in message.content:
        await message.delete()
        return await message.channel.send("🚫 Keine Links!")

    # 📈 XP SYSTEM
    user = message.author.id
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
    coins[ctx.author.id] = coins.get(ctx.author.id, 0) + 100
    await ctx.send("💰 +100 Coins")

@bot.command()
async def balance(ctx):
    await ctx.send(f"💰 Coins: {coins.get(ctx.author.id, 0)}")

# =========================
# ⚠️ MODERATION
# =========================
@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member):
    warns[member.id] = warns.get(member.id, 0) + 1
    await ctx.send(f"⚠️ Warn ({warns[member.id]}/3)")

    if warns[member.id] >= 3:
        await member.kick()
        await ctx.send("👢 automatisch gekickt")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send("👢 gekickt")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send("⛔ gebannt")

# =========================
# 🎟 TICKETS
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
        await ctx.send("🔒 schließen...")
        await asyncio.sleep(2)
        await ctx.channel.delete()

# =========================
# 🔐 VERIFICATION
# =========================
ROLE_NAME = "👥⠀×⠀COMMUNITY⠀×⠀👥"

@bot.command()
async def verify(ctx):
    code = random.randint(1000, 9999)
    verification_codes[ctx.author.id] = code

    await ctx.author.send(f"🔐 Code: {code}")
    await ctx.send("📩 DM gesendet!")

@bot.command()
async def code(ctx, number: int):
    if ctx.author.id not in verification_codes:
        return await ctx.send("❌ Kein Code")

    if verification_codes[ctx.author.id] == number:
        role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)

        if role:
            await ctx.author.add_roles(role)
            await ctx.send("✅ Verifiziert!")
        else:
            await ctx.send("❌ Rolle nicht gefunden!")

        del verification_codes[ctx.author.id]
    else:
        await ctx.send("❌ Falsch")

# =========================
# 🔊 MUSIC SYSTEM
# =========================
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("🔊 Joined")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left")

@bot.command()
async def play(ctx, url):
    if not ctx.author.voice:
        return await ctx.send("❌ Geh in Voice")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    music_queue.append(url)

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    if not music_queue:
        return

    url = music_queue.pop(0)

    ydl_opts = {"format": "bestaudio"}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio = info["url"]

    voice = ctx.voice_client
    source = await discord.FFmpegOpusAudio.from_probe(audio)

    def after(error):
        asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

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
# 🔐 ONDUTY
# =========================
@bot.command()
async def onduty(ctx, password: str):

    await ctx.message.delete()

    if password != ONDUTY_PASSWORD:
        return await ctx.send("❌ Falsch", delete_after=3)

    for role_name in ONDUTY_ROLES:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.author.add_roles(role)

    msg = await ctx.send("🟢 OnDuty aktiviert")
    await msg.delete(delay=5)

# =========================
# 🔴 OFFDUTY
# =========================
@bot.command()
async def offduty(ctx):

    removed = []

    for role_name in ONDUTY_ROLES:
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role and role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            removed.append(role_name)

    if removed:
        msg = await ctx.send("🔴 OffDuty aktiv")
        await msg.delete(delay=5)
    else:
        await ctx.send("❌ Keine Rollen")

# =========================
# 📜 HELP
# =========================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🤖 Bot Commands")

    embed.add_field(name="💰", value="!daily !balance", inline=False)
    embed.add_field(name="⚠️", value="!warn !kick !ban", inline=False)
    embed.add_field(name="🎟", value="!ticket !close", inline=False)
    embed.add_field(name="🔐", value="!verify !code", inline=False)
    embed.add_field(name="🔊", value="!join !play !skip !stop !leave", inline=False)
    embed.add_field(name="🟢 Duty", value="!onduty !offduty", inline=False)

    await ctx.send(embed=embed)

# =========================
# START
# =========================
bot.run(os.getenv("TOKEN"))
