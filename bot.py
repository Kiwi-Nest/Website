import discord
from discord.ext import tasks
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

# Track if logging is enabled
log_stats_enabled = True

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if log_stats_enabled and not log_stats.is_running():
        log_stats.start()

# Command to toggle the 24-hour logging loop
@client.event
async def on_message(message):
    global log_stats_enabled
    if message.author.bot:
        return
    if message.content.strip().lower() == "!togglelog":
        if log_stats.is_running():
            log_stats.stop()
            log_stats_enabled = False
            await message.channel.send("Logging loop stopped.")
        else:
            log_stats.start()
            log_stats_enabled = True
            await message.channel.send("Logging loop started.")

@tasks.loop(hours=24)  # log every 24 hours
async def log_stats():
    global log_stats_enabled
    if not log_stats_enabled:
        print("Logging is disabled. Skipping log_stats.")
        return
    guild = client.get_guild(GUILD_ID)
    if guild:
        member_count = guild.member_count
        now = datetime.now()
        timestamp = int(now.timestamp()) * 1000  # JS expects ms
        new_entry = {"date": timestamp, "value": member_count}

        try:
            with open("data.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        data.append(new_entry)

        with open("data.json", "w") as f:
            json.dump(data, f, indent=2)

        print(f"Logged: {member_count} members at {now}")

client.run(TOKEN)
