import asyncio
import importlib
from pyrogram import idle
from pyrogram.types import BotCommand
from pytgcalls.exceptions import NoActiveGroupCall
import config
from ShrutiMusic import LOGGER, app, userbot
from ShrutiMusic.core.call import Aviax
from ShrutiMusic.misc import sudo
from ShrutiMusic.plugins import ALL_MODULES
from ShrutiMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# Bot Commands List
COMMANDS = [
    BotCommand("start", "🚀 Start bot"),
    BotCommand("help", "❓ Help menu"),
    BotCommand("ping", "📡 Ping and system stats"),
    BotCommand("play", "🎵 Start streaming the requested track"),
    BotCommand("vplay", "📹 Start video streaming"),
    BotCommand("playforce", "⚠️ Force play audio track"),
    BotCommand("vplayforce", "⚠️ Force play video track"),
    BotCommand("pause", "⏸ Pause the stream"),
    BotCommand("resume", "▶️ Resume the stream"),
    BotCommand("skip", "⏭ Skip the current track"),
    BotCommand("end", "🛑 End the stream"),
    BotCommand("stop", "🛑 Stop the stream"),
    BotCommand("player", "🎛 Get interactive player panel"),
    BotCommand("queue", "📄 Show track queue"),
    BotCommand("auth", "➕ Add a user to auth list"),
    BotCommand("unauth", "➖ Remove a user from auth list"),
    BotCommand("authusers", "👥 Show list of auth users"),
    BotCommand("cplay", "📻 Channel audio play"),
    BotCommand("cvplay", "📺 Channel video play"),
    BotCommand("cplayforce", "🚨 Channel force audio play"),
    BotCommand("cvplayforce", "🚨 Channel force video play"),
    BotCommand("channelplay", "🔗 Connect group to channel"),
    BotCommand("loop", "🔁 Enable/disable loop"),
    BotCommand("stats", "📊 Bot stats"),
    BotCommand("shuffle", "🔀 Shuffle the queue"),
    BotCommand("seek", "⏩ Seek forward"),
    BotCommand("seekback", "⏪ Seek backward"),
    BotCommand("song", "🎶 Download song (mp3/mp4)"),
    BotCommand("speed", "⏩ Adjust audio playback speed (group)"),
    BotCommand("cspeed", "⏩ Adjust audio speed (channel)"),
    BotCommand("tagall", "📢 Tag everyone"),
    BotCommand("admins", "🛡 Tag all admins"),
    BotCommand("tgm", "🖼 Convert image to URL"),
    BotCommand("vid", "🎞 Download video from social media"),
    BotCommand("dice", "🎲 Roll a dice"),
    BotCommand("ludo", "🎲 Play ludo"),
    BotCommand("dart", "🎯 Throw a dart"),
    BotCommand("basket", "🏀 Play basketball"),
    BotCommand("football", "⚽ Play football"),
    BotCommand("slot", "🎰 Play slot"),
    BotCommand("jackpot", "🎰 Play jackpot"),
    BotCommand("bowling", "🎳 Play bowling"),
    BotCommand("ban", "🚫 Ban a user"),
    BotCommand("banall", "⚠️ Ban all users"),
    BotCommand("sban", "🧹 Delete & ban user"),
    BotCommand("tban", "⏳ Temporary ban"),
    BotCommand("unban", "✅ Unban a user"),
    BotCommand("warn", "⚠️ Warn a user"),
    BotCommand("swarn", "🧹 Delete & warn user"),
    BotCommand("rmwarns", "🗑 Remove all warnings"),
    BotCommand("warns", "📋 Show user warnings"),
    BotCommand("kick", "👢 Kick user"),
    BotCommand("skick", "🧹 Delete msg & kick"),
    BotCommand("purge", "🧽 Purge messages"),
    BotCommand("del", "❌ Delete message"),
    BotCommand("promote", "⬆️ Promote member"),
    BotCommand("fullpromote", "🚀 Full promote"),
    BotCommand("demote", "⬇️ Demote member"),
    BotCommand("pin", "📌 Pin message"),
    BotCommand("unpin", "❎ Unpin message"),
    BotCommand("unpinall", "🧹 Unpin all"),
    BotCommand("mute", "🔇 Mute user"),
    BotCommand("tmute", "⏱ Temp mute"),
    BotCommand("unmute", "🔊 Unmute"),
    BotCommand("zombies", "💀 Ban deleted accounts"),
    BotCommand("report", "🚨 Report to admins")
]

# Bot Bio and About
BOT_BIO = "ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ʙᴏᴛ ғᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴄʜᴀɴɴᴇʟ\n➻ sᴜᴘᴘᴏʀᴛ - 🔹 @ShrutiBots 🔹"
BOT_ABOUT = "🎧 This is a Powerful Telegram Music Bot for Group and Channel Streaming.\n🔹 Support: @ShrutiBots"

async def setup_bot_commands():
    """Setup bot commands, bio and about once during startup"""
    try:
        # Set bot commands
        await app.set_bot_commands(COMMANDS)
        LOGGER("ShrutiMusic").info("Bot commands set successfully!")
        
        # Set bot bio
        await app.set_chat_description(chat_id="me", description=BOT_BIO)
        LOGGER("ShrutiMusic").info("Bot bio set successfully!")
        
        # Set bot about
        await app.set_chat_description(chat_id="me", description=BOT_ABOUT)
        LOGGER("ShrutiMusic").info("Bot about set successfully!")
        
    except Exception as e:
        LOGGER("ShrutiMusic").error(f"Failed to set bot commands/bio: {str(e)}")

async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    await app.start()
    
    # Setup bot commands, bio and about once during startup
    await setup_bot_commands()

    for all_module in ALL_MODULES:
        importlib.import_module("ShrutiMusic.plugins" + all_module)

    LOGGER("ShrutiMusic.plugins").info("Successfully Imported Modules...")

    await userbot.start()
    await Aviax.start()

    try:
        await Aviax.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("ShrutiMusic").error(
            "Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass

    await Aviax.decorators()

    LOGGER("ShrutiMusic").info(
        "\x53\x68\x72\x75\x74\x69\x20\x4d\x75\x73\x69\x63\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\x0a\x0a\x44\x6f\x6e\x27\x74\x20\x66\x6f\x72\x67\x65\x74\x20\x74\x6f\x20\x76\x69\x73\x69\x74\x20\x40\x53\x68\x72\x75\x74\x69\x42\x6f\x74\x73"
    )

    await idle()

    await app.stop()
    await userbot.stop()
    LOGGER("ShrutiMusic").info("Stopping Shruti Music Bot...")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
