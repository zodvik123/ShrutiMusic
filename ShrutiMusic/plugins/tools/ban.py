import asyncio
from contextlib import suppress
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    ChatPrivileges,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from string import ascii_lowercase
from typing import Dict, Union
from ShrutiMusic import app
from ShrutiMusic.misc import SUDOERS
from ShrutiMusic.core.mongo import mongodb
from ShrutiMusic.utils.error import capture_err
from ShrutiMusic.utils.keyboard import ikb
from ShrutiMusic.utils.database import save_filter
from ShrutiMusic.utils.functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)
from ShrutiMusic.utils.permissions import adminsOnly, member_permissions
from config import BANNED_USERS

warnsdb = mongodb.warns

__MODULE__ = "Bᴀɴ"
__HELP__ = """
/ban - Ban A User
/banall - Ban All Users
/sban - Delete all messages of user that sended in group and ban the user
/tban - Ban A User For Specific Time
/unban - Unban A User
/warn - Warn A User
/swarn - Delete all the message sended in group and warn the user
/rmwarns - Remove All Warning of A User
/warns - Show Warning Of A User
/kick - Kick A User
/skick - Delete the replied message kicking its sender
/purge - Purge Messages
/purge [n] - Purge "n" number of messages from replied message
/del - Delete Replied Message
/promote - Promote A Member
/fullpromote - Promote A Member With All Rights
/demote - Demote A Member
/pin - Pin A Message
/unpin - unpin a message
/unpinall - unpinall messages
/mute - Mute A User
/tmute - Mute A User For Specific Time
/unmute - Unmute A User
/zombies - Ban Deleted Accounts
/report | @admins | @admin - Report A Message To Admins."""

async def int_to_alpha(user_id: int) -> str:
    alphabet = list(ascii_lowercase)[:10]
    text = ""
    user_id = str(user_id)
    for i in user_id:
        text += alphabet[int(i)]
    return text

async def get_warns_count() -> dict:
    chats_count = 0
    warns_count = 0
    async for chat in warnsdb.find({"chat_id": {"$lt": 0}}):
        for user in chat["warns"]:
            warns_count += chat["warns"][user]["warns"]
        chats_count += 1
    return {"chats_count": chats_count, "warns_count": warns_count}

async def get_warns(chat_id: int) -> Dict[str, int]:
    warns = await warnsdb.find_one({"chat_id": chat_id})
    if not warns:
        return {}
    return warns["warns"]

async def get_warn(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    if name in warns:
        return warns[name]

async def add_warn(chat_id: int, name: str, warn: dict):
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    warns[name] = warn
    await warnsdb.update_one(
        {"chat_id": chat_id}, {"$set": {"warns": warns}}, upsert=True
    )

async def remove_warns(chat_id: int, name: str) -> bool:
    warnsd = await get_warns(chat_id)
    name = name.lower().strip()
    if name in warnsd:
        del warnsd[name]
        await warnsdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"warns": warnsd}},
            upsert=True,
        )
        return True
    return False

@app.on_message(filters.command(["kick", "skick"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def kickFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user</b>", parse_mode="html")
    if user_id == app.id:
        return await message.reply_text("<b>I can't kick myself, I can leave if you want.</b>", parse_mode="html")
    if user_id in SUDOERS:
        return await message.reply_text("<b>You wanna kick the elevated one?</b>", parse_mode="html")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("<b>I can't kick an admin</b>", parse_mode="html")
    
    mention = (await app.get_users(user_id)).mention
    msg = f"""
<b>Kicked User:</b> {mention}
<b>Kicked By:</b> {message.from_user.mention if message.from_user else 'Anonymous'}
<b>Reason:</b> {reason or 'No reason provided'}"""
    
    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg, parse_mode="html")
    await asyncio.sleep(1)
    await message.chat.unban_member(user_id)
    if message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)

@app.on_message(
    filters.command(["ban", "sban", "tban"]) & ~filters.private & ~BANNED_USERS
)
@adminsOnly("can_restrict_members")
async def banFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)

    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")
    if user_id == app.id:
        return await message.reply_text("<b>I can't ban myself</b>", parse_mode="html")
    if user_id in SUDOERS:
        return await message.reply_text("<b>You wanna ban the elevated one?</b>", parse_mode="html")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("<b>I can't ban an admin</b>", parse_mode="html")

    try:
        mention = (await app.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "Anon"
        )

    msg = (
        f"<b>Banned User:</b> {mention}\n"
        f"<b>Banned By:</b> {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)
    if message.command[0] == "tban":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += f"<b>Banned For:</b> {time_value}\n"
        if temp_reason:
            msg += f"<b>Reason:</b> {temp_reason}"
        with suppress(AttributeError):
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg, parse_mode="html")
            else:
                await message.reply_text("<b>You can't use more than 99</b>", parse_mode="html")
        return
    if reason:
        msg += f"<b>Reason:</b> {reason}"
    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg, parse_mode="html")

@app.on_message(filters.command("unban") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def unban_func(_, message: Message):
    reply = message.reply_to_message
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text("<b>You cannot unban a channel</b>", parse_mode="html")

    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(f"<b>Unbanned!</b> {umention}", parse_mode="html")

@app.on_message(
    filters.command(["promote", "fullpromote"]) & ~filters.private & ~BANNED_USERS
)
@adminsOnly("can_promote_members")
async def promoteFunc(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")

    bot = (await app.get_chat_member(message.chat.id, app.id)).privileges
    if user_id == app.id:
        return await message.reply_text("<b>I can't promote myself.</b>", parse_mode="html")
    if not bot:
        return await message.reply_text("<b>I'm not an admin in this chat.</b>", parse_mode="html")
    if not bot.can_promote_members:
        return await message.reply_text("<b>I don't have enough permissions</b>", parse_mode="html")

    umention = (await app.get_users(user_id)).mention

    if message.command[0][0] == "f":
        await message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=bot.can_change_info,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=bot.can_restrict_members,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=bot.can_promote_members,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            ),
        )
        return await message.reply_text(f"<b>Fully promoted!</b> {umention}", parse_mode="html")

    await message.chat.promote_member(
        user_id=user_id,
        privileges=ChatPrivileges(
            can_change_info=False,
            can_invite_users=bot.can_invite_users,
            can_delete_messages=bot.can_delete_messages,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=bot.can_manage_chat,
            can_manage_video_chats=bot.can_manage_video_chats,
        ),
    )
    await message.reply_text(f"<b>Promoted!</b> {umention}", parse_mode="html")

@app.on_message(filters.command("purge") & ~filters.private)
@adminsOnly("can_delete_messages")
async def purgeFunc(_, message: Message):
    repliedmsg = message.reply_to_message
    await message.delete()

    if not repliedmsg:
        return await message.reply_text("<b>Reply to a message to purge from.</b>", parse_mode="html")

    cmd = message.command
    if len(cmd) > 1 and cmd[1].isdigit():
        purge_to = repliedmsg.id + int(cmd[1])
        if purge_to > message.id:
            purge_to = message.id
    else:
        purge_to = message.id

    chat_id = message.chat.id
    message_ids = []

    for message_id in range(repliedmsg.id, purge_to):
        message_ids.append(message_id)

        if len(message_ids) == 100:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,
            )
            message_ids = []

    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )

@app.on_message(filters.command("del") & ~filters.private)
@adminsOnly("can_delete_messages")
async def deleteFunc(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("<b>Reply to a message to delete it</b>", parse_mode="html")
    await message.reply_to_message.delete()
    await message.delete()

@app.on_message(filters.command("demote") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_promote_members")
async def demote(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")
    if user_id == app.id:
        return await message.reply_text("<b>I can't demote myself.</b>", parse_mode="html")
    if user_id in SUDOERS:
        return await message.reply_text("<b>You wanna demote the elevated one?</b>", parse_mode="html")
    try:
        member = await app.get_chat_member(message.chat.id, user_id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            await message.chat.promote_member(
                user_id=user_id,
                privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_chat=False,
                    can_manage_video_chats=False,
                ),
            )
            umention = (await app.get_users(user_id)).mention
            await message.reply_text(f"<b>Demoted!</b> {umention}", parse_mode="html")
        else:
            await message.reply_text("<b>The person you mentioned is not an admin.</b>", parse_mode="html")
    except Exception as e:
        await message.reply_text(f"<b>Error:</b> {e}", parse_mode="html")

@app.on_message(filters.command(["unpinall"]) & filters.group & ~BANNED_USERS)
@adminsOnly("can_pin_messages")
async def pin(_, message: Message):
    return await message.reply_text(
        "<b>Are you sure you want to unpin all messages?</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Yes", callback_data="unpin_yes"),
                    InlineKeyboardButton(text="No", callback_data="unpin_no"),
                ],
            ]
        ),
        parse_mode="html"
    )

@app.on_callback_query(filters.regex(r"unpin_(yes|no)"))
async def callback_query_handler(_, query: CallbackQuery):
    if query.data == "unpin_yes":
        await app.unpin_all_chat_messages(query.message.chat.id)
        return await query.message.edit_text("<b>All pinned messages have been unpinned.</b>", parse_mode="html")
    elif query.data == "unpin_no":
        return await query.message.edit_text("<b>Unpin of all pinned messages has been cancelled.</b>", parse_mode="html")

@app.on_message(filters.command(["pin", "unpin"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_pin_messages")
async def pin(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("<b>Reply to a message to pin/unpin it.</b>", parse_mode="html")
    r = message.reply_to_message
    if message.command[0][0] == "u":
        await r.unpin()
        return await message.reply_text(
            f"<b>Unpinned</b> <a href='{r.link}'>this message</a>.",
            disable_web_page_preview=True,
            parse_mode="html"
        )
    await r.pin(disable_notification=True)
    await message.reply(
        f"<b>Pinned</b> <a href='{r.link}'>this message</a>.",
        disable_web_page_preview=True,
        parse_mode="html"
    )
    msg = "Please check the pinned message: ~ " + f"<a href='{r.link}'>Check</a>"
    filter_ = dict(type="text", data=msg)
    await save_filter(message.chat.id, "~pinned", filter_)

@app.on_message(filters.command(["mute", "tmute"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def mute(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")
    if user_id == app.id:
        return await message.reply_text("<b>I can't mute myself.</b>", parse_mode="html")
    if user_id in SUDOERS:
        return await message.reply_text("<b>You wanna mute the elevated one?</b>", parse_mode="html")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("<b>I can't mute an admin</b>", parse_mode="html")
    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({"🚨  Unmute  🚨": f"unmute_{user_id}"})
    msg = (
        f"<b>Muted User:</b> {mention}\n"
        f"<b>Muted By:</b> {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0] == "tmute":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += f"<b>Muted For:</b> {time_value}\n"
        if temp_reason:
            msg += f"<b>Reason:</b> {temp_reason}"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(
                    user_id,
                    permissions=ChatPermissions(),
                    until_date=temp_mute,
                )
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg, reply_markup=keyboard, parse_mode="html")
            else:
                await message.reply_text("<b>You can't use more than 99</b>", parse_mode="html")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"<b>Reason:</b> {reason}"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg, reply_markup=keyboard, parse_mode="html")

@app.on_message(filters.command("unmute") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def unmute(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")
    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(f"<b>Unmuted!</b> {umention}", parse_mode="html")

@app.on_message(filters.command(["warn", "swarn"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def warn_user(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text("<b>I can't find that user</b>", parse_mode="html")
    if user_id == app.id:
        return await message.reply_text("<b>I can't warn myself</b>", parse_mode="html")
    if user_id in SUDOERS:
        return await message.reply_text("<b>I can't warn my manager's</b>", parse_mode="html")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("<b>I can't warn an admin</b>", parse_mode="html")
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({"🚨  Remove Warn  🚨": f"unwarn_{user_id}"})
    if warns:
        warns = warns["warns"]
    else:
        warns = 0
    if message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(f"<b>Number of warns of {mention} exceeded, banned!</b>", parse_mode="html")
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        msg = f"""
<b>Warned User:</b> {mention}
<b>Warned By:</b> {message.from_user.mention if message.from_user else 'Anonymous'}
<b>Reason:</b> {reason or 'No reason provided'}
<b>Warns:</b> {warns + 1}/3"""
        replied_message = message.reply_to_message
        if replied_message:
            message = replied_message
        await message.reply_text(msg, reply_markup=keyboard, parse_mode="html")
        await add_warn(chat_id, await int_to_alpha(user_id), warn)

@app.on_callback_query(filters.regex("unwarn") & ~BANNED_USERS)
async def remove_warning(_, cq: CallbackQuery):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "You don't have enough permissions to perform this action\n"
            + f"Permission needed: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer("User has no warnings.")
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__Warn removed by {from_user.mention}__"
    await cq.message.edit(text)

@app.on_message(filters.command("rmwarns") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def remove_warnings(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")
    mention = (await app.get_users(user_id)).mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if warns == 0 or not warns:
        await message.reply_text(f"<b>{mention} has no warnings.</b>", parse_mode="html")
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(f"<b>Removed warnings of {mention}.</b>", parse_mode="html")

@app.on_message(filters.command("warns") & ~filters.private & ~BANNED_USERS)
@capture_err
async def check_warns(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("<b>I can't find that user.</b>", parse_mode="html")
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    if warns:
        warns = warns["warns"]
    else:
        return await message.reply_text(f"<b>{mention} has no warnings.</b>", parse_mode="html")
    return await message.reply_text(f"<b>{mention} has {warns}/3 warnings</b>", parse_mode="html")

from pyrogram import filters
from ShrutiMusic import app
from ShrutiMusic.misc import SUDOERS
import asyncio
from pyrogram.errors import FloodWait

BOT_ID = app.id

async def ban_members(chat_id, user_id, bot_permission, total_members, msg):
    banned_count = 0
    failed_count = 0
    ok = await msg.reply_text(
        f"<b>Total members found:</b> {total_members}\n<b>Started banning...</b>",
        parse_mode="html"
    )
    
    while failed_count <= 30:
        async for member in app.get_chat_members(chat_id):
            if failed_count > 30:
                break
            
            try:
                if member.user.id != user_id and member.user.id not in SUDOERS:
                    await app.ban_chat_member(chat_id, member.user.id)
                    banned_count += 1

                    if banned_count % 5 == 0:
                        try:
                            await ok.edit_text(
                                f"<b>Banned {banned_count} members out of {total_members}</b>",
                                parse_mode="html"
                            )
                        except Exception:
                            pass

            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception:
                failed_count += 1

        if failed_count <= 30:
            await asyncio.sleep(5)
    
    await ok.edit_text(
        f"<b>Total banned:</b> {banned_count}\n<b>Failed bans:</b> {failed_count}\n<b>Stopped as failed bans exceeded limit.</b>",
        parse_mode="html"
    )

@app.on_message(filters.command("banall") & SUDOERS)
async def ban_all(_, msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    
    bot = await app.get_chat_member(chat_id, BOT_ID)
    bot_permission = bot.privileges.can_restrict_members
    
    if bot_permission:
        total_members = 0
        async for _ in app.get_chat_members(chat_id):
            total_members += 1
        
        await ban_members(chat_id, user_id, bot_permission, total_members, msg)
    
    else:
        await msg.reply_text(
            "<b>Either I don't have the right to restrict users or you are not in sudo users</b>",
            parse_mode="html"
        )

@app.on_message(filters.command("unbanme"))
async def unbanme(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("<b>Please provide the group ID.</b>", parse_mode="html")

        group_id = message.command[1]

        try:
            await client.unban_chat_member(group_id, message.from_user.id)
            
            try:
                member = await client.get_chat_member(group_id, message.from_user.id)
                if member.status == "member":
                    return await message.reply_text(
                        f"<b>You are already unbanned in that group.</b> You can join now by clicking here: {await get_group_link(client, group_id)}",
                        parse_mode="html"
                    )
            except UserNotParticipant:
                pass

            try:
                group_link = await get_group_link(client, group_id)
                await message.reply_text(
                    f"<b>I unbanned you in the group.</b> You can join now by clicking here: {group_link}",
                    parse_mode="html"
                )
            except InviteHashExpired:
                await message.reply_text("<b>I unbanned you in the group, but I couldn't provide a link to the group.</b>", parse_mode="html")
        except ChatAdminRequired:
            await message.reply_text("<b>I am not an admin in that group, so I cannot unban you.</b>", parse_mode="html")
    except Exception as e:
        await message.reply_text(f"<b>An error occurred:</b> {e}", parse_mode="html")

async def get_group_link(client, group_id):
    chat = await client.get_chat(group_id)
    if chat.username:
        return f"https://t.me/{chat.username}"
    else:
        invite_link = await client.export_chat_invite_link(group_id)
        return invite_link
