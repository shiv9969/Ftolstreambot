import os
import asyncio
from asyncio import TimeoutError
from biisal.bot import StreamBot
from biisal.utils.database import Database
from biisal.utils.human_readable import humanbytes
from biisal.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from biisal.utils.file_properties import get_name, get_hash, get_media_file_size

db = Database(Var.DATABASE_URL, Var.name)

msg_text = """<b>‣ ʏᴏᴜʀ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ! 😎

‣ Fɪʟᴇ ɴᴀᴍᴇ : <i>{}</i>
‣ Fɪʟᴇ ꜱɪᴢᴇ : {}

\n‣ ❤️ Powered By : @BoB_Files1✨🫶</b>"""

@StreamBot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!"
        )

    # Checking if user has joined updates channel
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="You are banned!\n\n  **Cᴏɴᴛᴀᴄᴛ Support [Support](https://t.me/assaulter_shiv) They Wɪʟʟ Hᴇʟᴘ Yᴏᴜ**",
                    disable_web_page_preview=True
                )
                return 
        except UserNotParticipant:
            await c.send_photo(
                chat_id=m.chat.id,
                photo="https://telegra.ph/file/d212055d9ab7bd2927f8e.jpg",
                caption="""<b>Hᴇʏ ᴛʜᴇʀᴇ!\n\nPʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ ! 😊\n\nDᴜᴇ ᴛᴏ sᴇʀᴠᴇʀ ᴏᴠᴇʀʟᴏᴀᴅ, ᴏɴʟʏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ sᴜʙsᴄʀɪʙᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʙᴏᴛ !</b>""",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Jᴏɪɴ ɴᴏᴡ 🚩", url=f"https://t.me/{Var.UPDATES_CHANNEL}")]]
                ),
            )
            return
        except Exception as e:
            await m.reply_text(e)
            return

    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

        await log_msg.reply_text(
            text=f"**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n"
                 f"**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`\n"
                 f"**Stream ʟɪɴᴋ :** {stream_link}",
            disable_web_page_preview=True,
            quote=True
        )

        await m.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m))),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("sᴛʀᴇᴀᴍ 🔺", url=stream_link),
                 InlineKeyboardButton('ᴅᴏᴡɴʟᴏᴀᴅ 🔻', url=online_link)],
                [InlineKeyboardButton("📂 Get File", callback_data=f"get_file_{log_msg.id}")]
            ])
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)

@StreamBot.on_callback_query(filters.regex(r"get_file_(\d+)"))
async def get_file_callback(c: Client, cb):
    file_id = int(cb.matches[0].group(1))
    try:
        log_msg = await c.get_messages(Var.BIN_CHANNEL, message_ids=file_id)
        if log_msg:
            await cb.message.reply_document(
                document=log_msg.document.file_id if log_msg.document else log_msg.video.file_id,
                caption=f"**Here is your requested file:** {log_msg.caption}",
                quote=True
            )
        else:
            await cb.answer("File not found!", show_alert=True)
    except Exception as e:
        await cb.answer(f"Error: {str(e)}", show_alert=True) 
