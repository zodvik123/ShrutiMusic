from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, CallbackQuery
import time
import config
from ShrutiMusic import app  # @WTF_WhyMeeh From TG

START_TIME = time.time()

def start_panel():
    buttons = [
        [
            InlineKeyboardButton(
                text="S_B_1",
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(
                text="S_B_2",
                url=config.SUPPORT_GROUP
            ),
        ],
        [
            InlineKeyboardButton(
                text="E_X_1",
                url="https://github.com/NoxxOP/ShrutiMusic/fork"
            ),
        ],
    ]
    return buttons

def private_panel(_):  # Added the underscore parameter
    buttons = [
        [
            InlineKeyboardButton(
                text="S_B_3",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(
                text="E_X_1",
                url="https://github.com/NoxxOP/ShrutiMusic/fork"
            ),
            InlineKeyboardButton(
                text="E_X_2",
                callback_data="show_status"
            ),
        ],
        [
            InlineKeyboardButton(text="S_B_6", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="S_B_5", user_id=config.OWNER_ID),
            InlineKeyboardButton(text="S_B_2", url=config.SUPPORT_GROUP),
        ],
        [
            InlineKeyboardButton(text="S_B_4", callback_data="settings_back_helper")
        ],
    ]
    return buttons

@app.on_callback_query(filters.regex("show_status"))
async def show_status_callback(client: Client, callback_query: CallbackQuery):
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    status_message = (
        "Bot Status:\n"
        "Status: Alive ✅\n"
        f"Uptime: {uptime_str}\n"
    )
    
    await callback_query.answer(text=status_message, show_alert=True)
