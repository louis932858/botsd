import discord
from discord.ext import commands
import os
import random

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command("help")

print("🔥 BOT FILE LOADED")

# =========================
# ONDUTY CONFIG
# =========================
ONDUTY_PASSWORD = "louis12"

ONDUTY_ROLES = [
    1482706290009706688,  # ★
    1482706289048948826   # 👑 CO OWNER
]

# =========================
# VERIFY SYSTEM
# =========================
verification_codes = {}

VERIFY_ROLE_NAME = "Verified"

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"🤖 BOT ONLINE: {bot.user}")

# =========================
# TEST COMMAND
# =========================
@bot.command()
async def test(ctx):
    await ctx.send("✅ Bot funktioniert")

# =========================
# ONDUTY
# =========================
@bot.command()
async def onduty(ctx, password: str):

    await ctx.message.delete()

    if password != ONDUTY_PASSWORD:
        return await ctx.send("❌ Falsches Passwort", delete_after=3)

    for role_id in ONDUTY_ROLES:
        role = ctx.guild.get_role(role_id)

        if role:
            await ctx.author.add_roles(role)

    msg = await ctx.send("🟢 OnDuty aktiviert")
    await msg.delete(delay=5)

# =========================
# OFFDUTY
# =========================
@bot.command()
async def offduty(ctx):

    removed = []

    for role_id in ONDUTY_ROLES:
        role = ctx.guild.get_role(role_id)

        if role and role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            removed.append(role.name)

    if removed:
        msg = await ctx.send("🔴 OffDuty deaktiviert")
        await msg.delete(delay=5)
    else:
        await ctx.send("❌ Du bist nicht OnDuty", delete_after=3)

# =========================
# VERIFY
# =========================
@bot.command()
async def verify(ctx):
    code = random.randint(1000, 9999)
    verification_codes[ctx.author.id] = code

    await ctx.author.send(f"🔐 Dein Code: {code}")
    await ctx.send("📩 Check deine DMs!")

@bot.command()
async def code(ctx, number: int):

    if ctx.author.id not in verification_codes:
        return await ctx.send("❌ Kein Code vorhanden")

    if verification_codes[ctx.author.id] == number:

        role = discord.utils.get(ctx.guild.roles, name=VERIFY_ROLE_NAME)

        if role:
            await ctx.author.add_roles(role)
            await ctx.send("✅ Verifiziert!")
        else:
            await ctx.send("❌ Rolle 'Verified' fehlt!")

        del verification_codes[ctx.author.id]

    else:
        await ctx.send("❌ Falscher Code")

# =========================
# ECONOMY
# =========================
coins = {}

@bot.command()
async def daily(ctx):
    coins[ctx.author.id] = coins.get(ctx.author.id, 0) + 100
    await ctx.send("💰 +100 Coins")

@bot.command()
async def balance(ctx):
    await ctx.send(f"💰 Coins: {coins.get(ctx.author.id, 0)}")

# =========================
# HELP
# =========================
@bot.command()
async def help(ctx):
    await ctx.send("""
🤖 BOT COMMANDS

💰 !daily / !balance
🔐 !verify / !code
🟢 !onduty <passwort>
🔴 !offduty
🧪 !test
""")

# =========================
# START BOT
# =========================
bot.run(os.getenv("TOKEN"))
