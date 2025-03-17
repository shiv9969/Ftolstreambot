import os
import asyncio
from asyncio import TimeoutError
from biisal.bot import StreamBot
from biisal.utils.database import Database
from biisal.utils.human_readable import humanbytes
from biisal.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant, MessageNotModified
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import re

from biisal.utils.file_properties import get_name, get_hash, get_media_file_size

# Re-add MY_PASS so it can be imported by other modules
MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
get_file_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

db = Database(Var.DATABASE_URL, Var.name)

msg_text = """<b>‣ ʏᴏᴜʀ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ! 😎

‣ Fɪʟᴇ ɴᴀᴍᴇ : <i>{}</i>
‣ Fɪʟᴇ ꜱɪᴢᴇ : {}

\n‣ ❤️ Powered By : @BoB_Files1✨🫶</b>"""

@StreamBot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        # Removed the notification in the channel

    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

        await m.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m))),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Stream", url=stream_link),
                 InlineKeyboardButton("📥 Download", url=online_link)],
                [InlineKeyboardButton("📂 Get File", callback_data=f"get_file_{log_msg.id}")],
                [InlineKeyboardButton("𝖲𝗁𝖺𝗋𝖾 𝖫𝗂𝗇𝗄 🔗", url=f"https://telegram.me/share/url?url={file_link}")]
            ])
        )
    except FloodWait as e:
        print(f"Sleeping for {e.x} seconds due to FloodWait.")
        await asyncio.sleep(e.x)

@StreamBot.on_callback_query(filters.regex(r"get_file_(\d+)"))
async def get_file_button_handler(c: Client, query: CallbackQuery):
    if match := re.search(r"get_file_(\d+)", query.data):
        message_id = int(match.group(1))
        user_id = query.from_user.id 
        chat_id = query.message.chat.id  
        
        file_msg = await c.get_messages(chat_id=Var.BIN_CHANNEL, message_ids=message_id)
        if not file_msg or (not file_msg.document and not file_msg.video and not file_msg.audio and not file_msg.photo):
            await query.answer("⚠ No File Found !", show_alert=True)
            return
        try:
            await file_msg.copy(chat_id=user_id)
            await query.answer("✅ File sent to your DM!", show_alert=True)
        except Exception as e:
            print(e)
            get_file_dict[user_id] = file_msg
            username = (await c.get_me()).username
            old_buttons = old_markup.inline_keyboard if message.reply_markup else []
            new_markup = old_buttons.append([InlineKeyboardButton("Start In PM", url=f"https://telegram.me/{username}?start=gf")])
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(new_markup))
    else:
        await query.answer("Invalid Callback Data !", show_alert=True)
        return

@StreamBot.on_message(filters.channel & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

        try:
            await bot.edit_message_reply_markup(
                chat_id=broadcast.chat.id,
                message_id=broadcast.id,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📺 Stream", url=stream_link),
                     InlineKeyboardButton("📥 Download", url=online_link)],
                    [InlineKeyboardButton("📂 Get File", callback_data=f"get_file_{log_msg.id}")],
                    [InlineKeyboardButton("𝖲𝗁𝖺𝗋𝖾 𝖫𝗂𝗇𝗄 🔗", url=f"https://telegram.me/share/url?url={file_link}")]
                ])
            )
        except MessageNotModified:
            pass

    except FloodWait as e:
        print(f"Sleeping for {e.x} seconds due to FloodWait.")
        await asyncio.sleep(e.x)
    except Exception as e:
        await bot.send_message(Var.BIN_CHANNEL, f"**Error:** `{e}`")
