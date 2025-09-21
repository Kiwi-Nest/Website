import discord
from discord.ext import tasks, commands
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to access guild.member_count

# Use commands.Bot instead of discord.Client for command handling
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Events ---
@bot.event
async def on_ready():
    """Event that runs when the bot is logged in and ready."""
    print(f"✅ Logged in as {bot.user}")
    
    # Sync hybrid commands with Discord to make them available as slash commands
    # This is faster than a global sync.
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print("🤖 Commands synced.")

    # Start the task loop if it's not already running
    if not log_stats.is_running():
        log_stats.start()
        print("🔁 Logging task started on launch.")

# --- Tasks ---
@tasks.loop(hours=24)
async def log_stats():
    """Logs the server's member count to a JSON file every 24 hours."""
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"❌ Error: Guild with ID {GUILD_ID} not found.")
        return

    member_count = guild.member_count
    now = datetime.now()
    # JavaScript-compatible timestamp in milliseconds
    timestamp = int(now.timestamp()) * 1000
    new_entry = {"date": timestamp, "value": member_count}

    try:
        # Open and read the existing data
        with open("data.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty/corrupt, start with an empty list
        data = []

    data.append(new_entry)

    # Write the updated data back to the file
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"📈 Logged: {member_count} members at {now.strftime('%Y-%m-%d %H:%M:%S')}")

# --- Commands ---
@bot.hybrid_command(name="togglelog", description="Starts or stops the 24-hour member logging task.")
@commands.has_permissions(administrator=True) # Restrict command to administrators
async def togglelog(ctx: commands.Context):
    """Toggles the 24-hour member logging task on or off."""
    # Check the task's current state directly instead of using a global variable
    if log_stats.is_running():
        log_stats.stop()
        await ctx.send("✅ Logging task has been **stopped**.")
        print("Logging task stopped by command.")
    else:
        log_stats.start()
        await ctx.send("✅ Logging task has been **started**.")
        print("Logging task started by command.")

@togglelog.error
async def togglelog_error(ctx: commands.Context, error):
    """Error handler for the togglelog command."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You must be an administrator to use this command.", ephemeral=True)
    else:
        await ctx.send("An unexpected error occurred. Please check the console.", ephemeral=True)
        print(f"Error in togglelog command: {error}") # Log other errors for debugging

# --- Run Bot ---
bot.run(TOKEN)
