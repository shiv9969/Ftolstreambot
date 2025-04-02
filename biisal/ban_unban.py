
import json
from pyrogram import Client, filters

BAN_LIST_FILE = "banned_users.json"
LOG_CHANNEL_ID = -1001001844691460  # Replace with your log channel ID
YOUR_ADMIN_ID = 1525203313  # Replace with your Telegram user ID

# Load banned users
def load_banned_users():
    try:
        with open(BAN_LIST_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save banned users
def save_banned_users(banned_users):
    with open(BAN_LIST_FILE, "w") as f:
        json.dump(banned_users, f)

banned_users = load_banned_users()

# Ban Command
@Client.on_message(filters.command("ban") & filters.user(YOUR_ADMIN_ID))
def ban_user(client, message):
    if len(message.command) < 2:
        message.reply_text("Usage: /ban <user_id>")
        return

    user_id = int(message.command[1])
    user = client.get_users(user_id)  # Get user details
    mention = user.mention  # Create mention link

    if user_id not in banned_users:
        banned_users.append(user_id)
        save_banned_users(banned_users)
        message.reply_text(f"🚨 {mention}, you are **banned** from this bot!")

        # Notify banned user
        try:
            client.send_message(
                user_id,
                f"Hi {mention}, I am the owner, Shiv.\n"
                "You are **banned** from using our bot because you violated our rules.\n\n"
                "If you want to appeal, message [@Assaulter_shiv](https://t.me/Assaulter_shiv) to resolve the matter."
            )
        except Exception:
            pass  # Ignore if user has blocked the bot

        # Send log to admin channel
        client.send_message(LOG_CHANNEL_ID, f"🚨 {mention} has been **banned** by {message.from_user.mention}.")
    else:
        message.reply_text("User is already banned.")

# Unban Command
@Client.on_message(filters.command("unban") & filters.user(YOUR_ADMIN_ID))
def unban_user(client, message):
    if len(message.command) < 2:
        message.reply_text("Usage: /unban <user_id>")
        return

    user_id = int(message.command[1])
    user = client.get_users(user_id)  # Get user details
    mention = user.mention  # Create mention link

    if user_id in banned_users:
        banned_users.remove(user_id)
        save_banned_users(banned_users)
        message.reply_text(f"✅ {mention}, you are **unbanned** now!")

        # Notify unbanned user
        try:
            client.send_message(
                user_id,
                f"Fine, {mention}, you are **unbanned** now!\n"
                "You can use the bot as much as you like. Enjoy! 🚀"
            )
        except Exception:
            pass  # Ignore if user has blocked the bot

        # Send log to admin channel
        client.send_message(LOG_CHANNEL_ID, f"✅ {mention} has been **unbanned** by {message.from_user.mention}.")
    else:
        message.reply_text("User is not banned.")

# Middleware: Block banned users
@Client.on_message(filters.private & filters.user(banned_users))
def block_banned_users(client, message):
    message.reply_text("🚫 You are banned from using this bot.")
