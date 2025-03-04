    except Exception as e:
        await query.answer(f"⚠ Error: {str(e)}", show_alert=True)
        
@StreamBot.on_message(filters.channel & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)

async def channel_receive_handler(bot, broadcast):

try:

    log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)

    stream_link = f"{Var.URL}watch/{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

    online_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"



    await log_msg.reply_text(

        text=f"**Channel Name:** `{broadcast.chat.title}`\n"

             f"**Channel ID:** `{broadcast.chat.id}`\n"

             f"**Stream Link:** {stream_link}",

        quote=True

    )



    try:

        await bot.edit_message_reply_markup(

            chat_id=broadcast.chat.id,

            message_id=broadcast.id,

            reply_markup=InlineKeyboardMarkup([

                [InlineKeyboardButton("📺 Stream", url=stream_link),

                 InlineKeyboardButton("📥 Download", url=online_link)],

                [InlineKeyboardButton("📂 Get File", callback_data=f"get_file_{log_msg.id}")]

            ])

        )

    except MessageNotModified:

        pass



except FloodWait as e:

    print(f"Sleeping for {e.x} seconds due to FloodWait.")

    await asyncio.sleep(e.x)

except Exception as e:

    await bot.send_message(Var.BIN_CHANNEL, f"**Error:** `{e}`")

