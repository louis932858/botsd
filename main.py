import discord
from discord.ext import commands
import os

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")

ONDUTY_PASSWORD = "louis12"

ONDUTY_ROLES = [
    1482706290009706688,  # ★
    1482706289048948826   # 👑 CO OWNER
]

waiting_password = {}

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 BOT ONLINE: {bot.user}")

# =========================
# TEST
# =========================
@bot.command()
async def test(ctx):
    await ctx.send("✅ Bot funktioniert")

# =========================
# ONDUTY (DM PASSWORD)
# =========================
@bot.command()
async def onduty(ctx):

    try:
        dm = await ctx.author.create_dm()
        await dm.send("🔐 Bitte gib dein OnDuty Passwort ein:")
        waiting_password[ctx.author.id] = ctx.guild.id
        await ctx.send("📩 Ich habe dir eine DM geschickt!")
    except:
        await ctx.send("❌ Konnte keine DM senden")

# =========================
# OFFDUTY
# =========================
@bot.command()
async def offduty(ctx):

    removed = False

    for role_id in ONDUTY_ROLES:
        role = ctx.guild.get_role(role_id)

        if role and role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            removed = True

    if removed:
        await ctx.send("🔴 OffDuty aktiviert")
    else:
        await ctx.send("❌ Du bist nicht OnDuty")

# =========================
# PASSWORD HANDLER
# =========================
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    if user_id in waiting_password:

        if message.guild is None:  # nur DM
            guild_id = waiting_password[user_id]

            if message.content == ONDUTY_PASSWORD:

                guild = discord.utils.get(bot.guilds, id=guild_id)
                member = guild.get_member(user_id)

                if member:
                    for role_id in ONDUTY_ROLES:
                        role = guild.get_role(role_id)
                        if role:
                            await member.add_roles(role)

                    await message.channel.send("🟢 OnDuty aktiviert!")
                else:
                    await message.channel.send("❌ User nicht gefunden")

            else:
                await message.channel.send("❌ Falsches Passwort")

            del waiting_password[user_id]
            return

    await bot.process_commands(message)

# =========================
# START BOT
# =========================
bot.run(TOKEN)
