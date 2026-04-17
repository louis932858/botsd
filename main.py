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
        await message.channel.send("🚫 Keine Links erlaubt!")
        return

    # 📈 XP
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
        await ctx.send("👢 automatisch gekickt!")

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

@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send("🎭 Rolle gegeben")

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

    await channel.send("🎟 Ticket erstellt!")
    await ctx.send("✅ Ticket erstellt!")

@bot.command()
async def close(ctx):
    if "ticket" in ctx.channel.name:
        await ctx.send("🔒 Schließen...")
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

    await ctx.author.send(f"🔐 Dein Code: {code}")
    await ctx.send("📩 DM gesendet!")

@bot.command()
async def code(ctx, number: int):
    if ctx.author.id not in verification_codes:
        return await ctx.send("❌ Kein Code!")

    if verification_codes[ctx.author.id] == number:
        role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)

        if role:
            await ctx.author.add_roles(role)
            await ctx.send("✅ Verifiziert!")
        else:
            await ctx.send("❌ Rolle nicht gefunden!")

        del verification_codes[ctx.author.id]
    else:
        await ctx.send("❌ Falsch!")

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
# 📜 HELP
# =========================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🤖 Bot Commands", color=discord.Color.blue())

    embed.add_field(name="💰 Economy", value="!daily !balance", inline=False)
    embed.add_field(name="⚠️ Moderation", value="!warn !kick !ban !role", inline=False)
    embed.add_field(name="🎟 Tickets", value="!ticket !close", inline=False)
    embed.add_field(name="🔐 Verify", value="!verify !code", inline=False)
    embed.add_field(name="🔊 Music", value="!join !play !skip !stop !leave", inline=False)
    embed.add_field(name="🤖 AI", value="!ai", inline=False)

    await ctx.send(embed=embed)

# =========================
# START BOT
# =========================
bot.run(os.getenv("TOKEN"))
