import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
import os

@Client.on_message(filters.command("gitupdate") & filters.private)
async def git_update_force(client, message: Message):
    await message.reply_text("🔐 Please send your **GitHub Personal Access Token (Classic)**:")

    # Wait for token from user
    token_msg = await client.listen(message.chat.id)
    token = token_msg.text.strip()

    await message.reply_text("📦 Now send your **GitHub Repo URL** (e.g., https://github.com/username/repo):")
    repo_msg = await client.listen(message.chat.id)
    repo_url = repo_msg.text.strip()

    # Extract repo slug
    try:
        repo_slug = repo_url.split("github.com/")[1]
    except IndexError:
        await message.reply_text("❌ Invalid repo URL.")
        return

    await message.reply_text("🔄 Syncing your repo with upstream... Please wait.")

    try:
        # Remove current .git if exists (clean start)
        if os.path.exists(".git"):
            subprocess.run(["rm", "-rf", ".git"], check=True)

        # Re-init git and set your repo as origin
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "remote", "add", "origin", f"https://{token}@github.com/{repo_slug}.git"], check=True)
        subprocess.run(["git", "remote", "add", "upstream", "https://github.com/NoxxOP/ShrutiMusic.git"], check=True)

        # Fetch and force reset to upstream
        subprocess.run(["git", "fetch", "upstream"], check=True)
        subprocess.run(["git", "reset", "--hard", "upstream/main"], check=True)

        # Force push to user's repo
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)

        await message.reply_text("✅ Your repo has been fully synced with the main repo.\n\n🔗 Now it's identical to: https://github.com/NoxxOP/ShrutiMusic")

    except subprocess.CalledProcessError as e:
        await message.reply_text(f"❌ Error during update:\n<code>{str(e)}</code>")
