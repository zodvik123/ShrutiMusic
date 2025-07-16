from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import os
from ShrutiMusic import app

# Token aur Repo store karne ke liye temp dict
user_sessions = {}

# Step 1: Start command
@app.on_message(filters.command("gitupdate") & filters.private)
async def git_update_command(client: Client, message: Message):
    await message.reply_text("🔐 <b>Please send your <u>GitHub Classic Token</u></b>.\n\n<i>(Don't worry, it's temporary and won't be saved.)</i>")
    user_sessions[message.from_user.id] = {"step": "awaiting_token"}

@app.on_message(filters.private & filters.text)
async def handle_updates(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_sessions:
        return

    step = user_sessions[user_id].get("step")

    if step == "awaiting_token":
        user_sessions[user_id]["token"] = message.text.strip()
        user_sessions[user_id]["step"] = "awaiting_repo"
        await message.reply_text("📁 <b>Now send your <u>forked repo URL</u> (e.g. https://github.com/NoxxOP/ShrutiMusic)</b>")

    # Step: Repo received
    elif step == "awaiting_repo":
        token = user_sessions[user_id]["token"]
        repo_url = message.text.strip()

        if "github.com" not in repo_url:
            await message.reply_text("❌ Invalid URL. Please send a valid GitHub repo URL.")
            return

        try:
            username, reponame = repo_url.split("github.com/")[1].split("/", 1)
            reponame = reponame.strip("/")
        except:
            await message.reply_text("❌ Couldn't parse the repo URL.")
            return

        await message.reply_text("🔄 Starting update... please wait...")

        # Git clone
        try:
            subprocess.run(["rm", "-rf", "temp_git"], check=True)
            subprocess.run(["git", "clone", f"https://{token}@github.com/{username}/{reponame}.git", "temp_git"], check=True)

            os.chdir("temp_git")
            subprocess.run(["git", "remote", "add", "upstream", "https://github.com/NoxxOP/ShrutiMusic.git"], check=True)
            subprocess.run(["git", "fetch", "upstream"], check=True)
            subprocess.run(["git", "merge", "upstream/main", "-m", "Sync with original repo"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            os.chdir("..")
            subprocess.run(["rm", "-rf", "temp_git"], check=True)

            await message.reply_text("✅ <b>Your repo has been updated with the main repo.</b>\n\nCheck: https://github.com/" + username + "/" + reponame)
        except subprocess.CalledProcessError as e:
            await message.reply_text(f"❌ Error occurred during update:\n<code>{e}</code>")

        # Clear session
        user_sessions.pop(user_id, None)
