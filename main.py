import discord
from discord.ext import commands
import random
import datetime
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 📊 DATABASE (simple RAM)
# =========================
coins = {}
levels = {}

# =========================
# 🧾 LOG CHANNEL
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

# =========================
# 💰 ECONOMY SYSTEM
# =========================
@bot.command()
async def daily(ctx):
    user = ctx.author.id
    coins[user] = coins.get(user, 0) + 100
    await ctx.send("💰 Du hast 100 Coins bekommen!")

@bot.command()
async def balance(ctx):
    user = ctx.author.id
    await ctx.send(f"💰 Du hast {coins.get(user, 0)} Coins")

@bot.command()
async def shop(ctx):
    await ctx.send("🛒 Shop: !buy sword (500 coins)")

@bot.command()
async def buy(ctx, item):
    user = ctx.author.id
    if item == "sword":
        if coins.get(user, 0) >= 500:
            coins[user] -= 500
            await ctx.send("⚔️ Sword gekauft!")
        else:
            await ctx.send("❌ Nicht genug Coins")

# =========================
# 📊 LEVEL SYSTEM
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = message.author.id
    levels[user] = levels.get(user, 0) + 1

    if levels[user] % 10 == 0:
        await message.channel.send(f"📊 {message.author.mention} Level Up!")

    await bot.process_commands(message)

# =========================
# 🎟 VERIFICATION (CAPTCHA)
# =========================
@bot.command()
async def verify(ctx):
    num = random.randint(1000, 9999)
    await ctx.send(f"🔐 Schreibe diese Zahl: **{num}**")

    def check(m):
        return m.author == ctx.author

    msg = await bot.wait_for("message", check=check)

    if msg.content == str(num):
        role = discord.utils.get(ctx.guild.roles, name="Verified")
        if role:
            await ctx.author.add_roles(role)
        await ctx.send("✅ Verifiziert!")
    else:
        await ctx.send("❌ Falsch")

# =========================
# 🤖 SIMPLE AI CHAT (offline fake AI)
# =========================
@bot.command()
async def ai(ctx, *, msg):
    answers = [
        "Ich denke ja 🤖",
        "Nein eher nicht ❌",
        "Interessante Frage!",
        "Das weiß ich nicht genau 🤔",
        "Sehr wahrscheinlich ✅"
    ]
    await ctx.send(random.choice(answers))

# =========================
# 🧾 LOGS
# =========================
@bot.event
async def on_member_join(member):
    await log(member.guild, f"{member} ist gejoined")

@bot.event
async def on_member_remove(member):
    await log(member.guild, f"{member} hat verlassen")

# =========================
# 🎟 START BOT
# =========================
