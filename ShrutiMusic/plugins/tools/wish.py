import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message
from ShrutiMusic import app

# Global dictionary to track active chats for all tagging types
active_chats = {}

# Message templates for different times of day
GM_MESSAGES = [
    "🌞 Gᴏᴏᴅ Mᴏʀɴɪɴɢ 🌼 {mention}",
    "☕ Rise and Shine, {mention}!",
    "🌄 Sᴜʀᴀᴊ Nɪᴋʜʀᴀ, Tᴜᴍʜᴀʀᴀ Dɪɴ Sᴜʙʜ Hᴏ {mention}",
    "🌻 Nᴇᴇᴛʜ Kʜᴀᴛᴀᴍ, Aʙ Kᴀᴀᴍ Sʜᴜʀᴜ {mention}",
    "💫 Jᴀɢᴏ Mᴇʀᴇ Sʜᴇʀᴏ! {mention}",
    "🕊️ Sᴜᴋʜ Sᴀʙʜᴀ Gᴏᴏᴅ Mᴏʀɴɪɴɢ {mention}",
    "🌅 Nᴀʏɪ Sᴜʙᴀʜ, Nᴀʏᴇ Sᴀᴘɴᴇ {mention}",
    "🌸 Pʜᴜᴀʟᴏɴ Sᴇ Bʜᴀʀᴀ Yᴇʜ Sᴜʙᴀʜ {mention}",
    "⭐ Uᴛʜᴏ Mᴇʀᴇ Sɪᴛᴀʀᴏ, Dɪɴ Sᴜʜᴀᴠᴀɴᴀ Hᴏ {mention}",
    "🌺 Kʜᴜsʜɪʏᴏɴ Sᴇ Bʜᴀʀᴀ Hᴏ Yᴇʜ Dɪɴ {mention}",
    "🦋 Tɪᴛʟɪʏᴏɴ Kɪ Tᴀʀᴀʜ Uᴅᴏ Aᴀᴊ {mention}",
    "🌈 Rᴀɴɢ Bʜᴀʀᴀ Hᴏ Yᴇʜ Dɪɴ Tᴜᴍʜᴀʀᴀ {mention}",
    "🎵 Pᴀᴋsʜɪʏᴏɴ Kᴀ Gᴀᴀɴᴀ Sᴜɴᴋᴇ Uᴛʜᴏ {mention}",
    "🌤️ Dʜᴜᴀɴ Kᴀ Gɪʟᴀᴀs Aᴜʀ Tᴜᴍʜᴀʀɪ Hᴀɴsɪ {mention}",
    "🌟 Cʜᴀᴀɴᴅ Sɪᴛᴀʀᴇ Bᴏʟᴇ - Gᴏᴏᴅ Mᴏʀɴɪɴɢ {mention}",
    "💐 Hᴀʀ Kᴀᴀᴍ Mᴇɪɴ Kᴀᴀᴍʏᴀʙɪ Mɪʟᴇ {mention}"
]

GA_MESSAGES = [
    "🌞 Gᴏᴏᴅ Aғᴛᴇʀɴᴏᴏɴ ☀️ {mention}",
    "🍵 Cʜᴀɪ Pɪ Lᴏ, Aғᴛᴇʀɴᴏᴏɴ Hᴏ Gᴀʏɪ {mention}",
    "🌤️ Hᴀʟᴋɪ Dᴏᴘʜᴀʀ, Aᴜʀ Tᴜᴍʜᴀʀᴀ Nᴀᴀᴍ 💌 {mention}",
    "😴 Sᴏɴᴀ Mᴀᴛ, Kᴀᴀᴍ Kᴀʀᴏ 😜 {mention}",
    "📢 Hᴇʏ {mention}, Gᴏᴏᴅ Aғᴛᴇʀɴᴏᴏɴ!",
    "🌅 Dᴏᴘʜᴀʀ Kᴀ Sᴜʀᴀᴊ Tᴇᴢ Hᴀɪ {mention}",
    "🥗 Kʜᴀᴀɴᴀ Kʜᴀʏᴀ Kᴇ Nᴀʜɪ {mention}?",
    "☀️ Tᴇᴢ Dʜᴜᴀᴘ Mᴇɪɴ Tʜᴀɴᴅᴀ Pᴀᴀɴɪ Pɪʏᴏ {mention}",
    "🌻 Dᴏᴘʜᴀʀ Kᴀ Aʀᴀᴀᴍ Kᴀʀᴏ {mention}",
    "🍃 Pᴀᴘᴇᴅ Kᴇ Nᴇᴇᴄʜᴇ Bᴀɪᴛʜᴋᴇ Bᴀᴀᴛᴇɪɴ {mention}",
    "🌸 Lᴜɴᴄʜ Kᴀ Tɪᴍᴇ Hᴏ Gᴀʏᴀ {mention}",
    "🦋 Dᴏᴘʜᴀʀ Kɪ Mᴀsᴛɪ Kᴀʀᴏ {mention}",
    "🍉 Tᴀʀʙᴜᴊ Kʜᴀᴀᴋᴇ Tʜᴀɴᴅᴀ Hᴏ Jᴀᴏ {mention}",
    "🌺 Aᴀsᴍᴀɴ Bʜɪ Sᴀᴀғ Hᴀɪ Aᴀᴊ {mention}",
    "🎵 Gᴜɴɢᴜɴᴀᴛᴇ Hᴜᴇ Kᴀᴀᴍ Kᴀʀᴏ {mention}",
    "🌈 Rᴀɴɢ Bɪʀᴀɴɢᴀ Dᴏᴘʜᴀʀ {mention}"
]

GN_MESSAGES = [
    "🌙 Gᴏᴏᴅ Nɪɢʜᴛ {mention}",
    "💤 Sᴏɴᴇ Cʜᴀʟᴏ, Kʜᴀᴡᴀʙᴏɴ Mᴇɪɴ Mɪʟᴛᴇ Hᴀɪɴ 😴 {mention}",
    "🌌 Aᴀsᴍᴀɴ Bʜɪ Sᴏ Gᴀʏᴀ {mention}, Aʙ Tᴜᴍʜɪ Bʜɪ Sᴏ Jᴀᴏ!",
    "✨ Rᴀᴀᴛ Kᴀ Sᴀᴋᴏᴏɴ Tᴜᴍʜᴇɪ Mɪʟᴇ {mention}",
    "🌃 Gᴏᴏᴅ Nɪɢʜᴛ & Sᴡᴇᴇᴛ Dʀᴇᴀᴍs {mention}",
    "🌟 Sɪᴛᴀʀᴏɴ Kᴇ Sᴀᴀᴛʜ Sᴏɴᴀ {mention}",
    "🕊️ Cᴀᴀɴᴅ Kɪ Rᴏsʜɴɪ Mᴇɪɴ Aᴀʀᴀᴀᴍ {mention}",
    "🎭 Sᴀᴘɴᴏɴ Kᴀ Rᴀᴀᴊᴀ Bᴀɴᴋᴇ Sᴏɴᴀ {mention}",
    "🌺 Rᴀᴀᴛ Kᴇ Pʜᴜᴀʟᴏɴ Sᴇ Mɪʟᴏ {mention}",
    "💫 Cʜᴀᴀɴᴅ Mᴀᴀᴍᴀ Kʜᴀᴀɴɪ Sᴜɴᴀᴛᴇ Hᴀɪɴ {mention}",
    "🎵 Lᴏʀɪ Kᴇ Sᴀᴀᴛʜ Sᴏɴᴀ {mention}",
    "🌸 Sᴀᴀʀᴇ Gᴀᴍ Bʜᴜᴀʟᴀᴋᴇ Sᴏɴᴀ {mention}",
    "🦋 Tɪᴛʟɪʏᴏɴ Kᴇ Sᴀᴀᴛʜ Sᴀᴘɴᴇ {mention}",
    "🌈 Rᴀɴɢ Bɪʀᴀɴɢᴇ Kʜᴀᴀʙ Dᴇᴋʜɴᴀ {mention}",
    "🕯️ Dɪʏᴇ Kɪ Rᴏsʜɴɪ Mᴇɪɴ Sᴏɴᴀ {mention}",
    "🌅 Kᴀʟ Pʜɪʀ Mɪʟᴇɴɢᴇ Sᴜʙᴀʜ {mention}"
]

# Helper function to get all non-bot, non-deleted users from a chat
async def get_chat_users(chat_id):
    """Get all valid users from a chat (excluding bots and deleted accounts)"""
    users = []
    async for member in app.get_chat_members(chat_id):
        if member.user.is_bot or member.user.is_deleted:
            continue
        users.append(member.user)
    return users

# Generic tagging function
async def tag_users(chat_id, messages, tag_type):
    """Generic function to tag users with specified messages"""
    users = await get_chat_users(chat_id)
    
    for i in range(0, len(users), 5):
        # Check if tagging was stopped
        if chat_id not in active_chats:
            break
            
        batch = users[i:i+5]
        mentions = " ".join([f"[{u.first_name}](tg://user?id={u.id})" for u in batch])
        msg = random.choice(messages).format(mention=mentions)
        
        await app.send_message(chat_id, msg, disable_web_page_preview=True)
        await asyncio.sleep(2)
    
    # Clean up and send completion message
    active_chats.pop(chat_id, None)
    await app.send_message(chat_id, f"✅ {tag_type} Tᴀɢɢɪɴɢ Dᴏɴᴇ!")

# =================== GOOD MORNING COMMANDS ===================

@app.on_message(filters.command("gmtag") & filters.group)
async def gmtag(_, message: Message):
    """Start Good Morning tagging"""
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        return await message.reply("⚠️ Gᴏᴏᴅ Mᴏʀɴɪɴɢ Tᴀɢɢɪɴɢ Aʟʀᴇᴀᴅʏ Rᴜɴɴɪɴɢ.")
    
    active_chats[chat_id] = True
    await message.reply("☀️ Gᴏᴏᴅ Mᴏʀɴɪɴɢ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...")
    
    await tag_users(chat_id, GM_MESSAGES, "Gᴏᴏᴅ Mᴏʀɴɪɴɢ")

@app.on_message(filters.command("gmstop") & filters.group)
async def gmstop(_, message: Message):
    """Stop Good Morning tagging"""
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        del active_chats[chat_id]
        await message.reply("🛑 Gᴏᴏᴅ Mᴏʀɴɪɴɢ Tᴀɢɢɪɴɢ Sᴛᴏᴘᴘᴇᴅ.")
    else:
        await message.reply("❌ Nᴏᴛʜɪɴɢ Rᴜɴɴɪɴɢ.")

# =================== GOOD AFTERNOON COMMANDS ===================

@app.on_message(filters.command("gatag") & filters.group)
async def gatag(_, message: Message):
    """Start Good Afternoon tagging"""
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        return await message.reply("⚠️ Aғᴛᴇʀɴᴏᴏɴ Tᴀɢɢɪɴɢ Aʟʀᴇᴀᴅʏ Oɴ.")
    
    active_chats[chat_id] = True
    await message.reply("☀️ Aғᴛᴇʀɴᴏᴏɴ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...")
    
    await tag_users(chat_id, GA_MESSAGES, "Aғᴛᴇʀɴᴏᴏɴ")

@app.on_message(filters.command("gastop") & filters.group)
async def gastop(_, message: Message):
    """Stop Good Afternoon tagging"""
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        del active_chats[chat_id]
        await message.reply("🛑 Aғᴛᴇʀɴᴏᴏɴ Tᴀɢɢɪɴɢ Sᴛᴏᴘᴘᴇᴅ.")
    else:
        await message.reply("❌ Nᴏᴛʜɪɴɢ Rᴜɴɴɪɴɢ.")

# =================== GOOD NIGHT COMMANDS ===================

@app.on_message(filters.command("gntag") & filters.group)
async def gntag(_, message: Message):
    """Start Good Night tagging"""
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        return await message.reply("⚠️ Nɪɢʜᴛ Tᴀɢɢɪɴɢ Aʟʀᴇᴀᴅʏ Oɴ.")
    
    active_chats[chat_id] = True
    await message.reply("🌙 Nɪɢʜᴛ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...")
    
    await tag_users(chat_id, GN_MESSAGES, "Gᴏᴏᴅ Nɪɢʜᴛ")

@app.on_message(filters.command("gnstop") & filters.group)
async def gnstop(_, message: Message):
    """Stop Good Night tagging"""
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        del active_chats[chat_id]
        await message.reply("🛑 Nɪɢʜᴛ Tᴀɢɢɪɴɢ Sᴛᴏᴘᴘᴇᴅ.")
    else:
        await message.reply("❌ Nᴏᴛʜɪɴɢ Rᴜɴɴɪɴɢ.")

# =================== UTILITY COMMANDS ===================

@app.on_message(filters.command("stopall") & filters.group)
async def stopall(_, message: Message):
    """Stop all active tagging in current chat"""
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        del active_chats[chat_id]
        await message.reply("🛑 Aʟʟ Tᴀɢɢɪɴɢ Sᴛᴏᴘᴘᴇᴅ.")
    else:
        await message.reply("❌ Nᴏ Aᴄᴛɪᴠᴇ Tᴀɢɢɪɴɢ Fᴏᴜɴᴅ.")

@app.on_message(filters.command("taghelp") & filters.group)
async def taghelp(_, message: Message):
    """Show help message for tagging commands"""
    help_text = """
🏷️ **Tagging Commands Help**

**Good Morning:**
• `/gmtag` - Start Good Morning tagging
• `/gmstop` - Stop Good Morning tagging

**Good Afternoon:**
• `/gatag` - Start Good Afternoon tagging  
• `/gastop` - Stop Good Afternoon tagging

**Good Night:**
• `/gntag` - Start Good Night tagging
• `/gnstop` - Stop Good Night tagging

**Utility:**
• `/stopall` - Stop all active tagging
• `/taghelp` - Show this help message

**Note:** Only one tagging session can run per chat at a time.
"""
    await message.reply(help_text)
