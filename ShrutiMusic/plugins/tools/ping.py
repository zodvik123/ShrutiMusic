# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar
#
# All rights reserved.
#
# This code is the intellectual property of Nand Yaduwanshi.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: badboy809075@gmail.com


from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from ShrutiMusic import app
from ShrutiMusic.misc import SUDOERS
from ShrutiMusic.utils.ping import bot_sys_stats
from ShrutiMusic.utils import bot_sys_stats
from ShrutiMusic.utils.inline import supp_markup
from ShrutiMusic.utils.ping import Aviax
from ShrutiMusic.platforms.Carbon import CarbonAPI
from config import BANNED_USERS
from strings.helpers import language

@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    temp = await message.reply("⚡ <b>Pinging...</b>")

    # Measure latency
    start = datetime.now()
    pytgping = await Aviax.ping()
    uptime, cpu, ram, disk = await bot_sys_stats()
    latency = (datetime.now() - start).microseconds / 1000

    # Carbon Text
    carbon_text = f"""
╭⎯⎯⎯⎯⎯⎯⎯⎯〔 ⚙️ ᴘɪɴɢ ʀᴇᴘᴏʀᴛ 〕⎯⎯⎯⎯⎯⎯⎯⎯╮

├⏱ ᴘʏ-ᴛɢ ᴘɪɴɢ: {pytgping} ms
├⚡ ʙᴏᴛ ʟᴀᴛᴇɴᴄʏ: {latency:.2f} ms
├🧠 ʀᴀᴍ ᴜsᴀɢᴇ: {ram}
├💾 ᴅɪsᴋ ᴜsᴀɢᴇ: {disk}
├🖥️ ᴄᴘᴜ ᴜsᴀɢᴇ: {cpu}
├🔋 ᴜᴘᴛɪᴍᴇ: {uptime}

╰⎯⎯⎯⎯⎯⎯〔 {app.mention} 〕⎯⎯⎯⎯⎯⎯╯
"""

    # Generate Carbon Image
    try:
        carbon = CarbonAPI()
        image_path = await carbon.generate(carbon_text, message.from_user.id)
    except Exception as e:
        await temp.edit("❌ Failed to generate carbon image.")
        return

    await temp.delete()
    await message.reply_photo(
        photo=image_path,
        caption=f"✨ <b>ᴘɪɴɢ ʀᴇᴘᴏʀᴛ ɪs ʀᴇᴀᴅʏ,</b> {message.from_user.mention}!",
        reply_markup=supp_markup(_)
    )
