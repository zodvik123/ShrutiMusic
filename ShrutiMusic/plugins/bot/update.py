import subprocess
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import os

@Client.on_message(filters.command("gitupdate") & filters.private)
async def git_update_force(client, message: Message):
    try:
        # Request GitHub Personal Access Token
        await message.reply_text(
            "🔐 Please send your <b>GitHub Personal Access Token (Classic)</b>:",
            disable_web_page_preview=True
        )
        
        # Wait for token from user
        token_msg = await client.listen(message.chat.id, timeout=120)
        token = token_msg.text.strip()
        
        # Validate token format (basic check)
        if not token or len(token) < 20:
            await message.reply_text("❌ Invalid token format. Please try again.")
            return
            
        await message.reply_text(
            "📦 Now send your <b>GitHub Repo URL</b> (e.g., https://github.com/username/repo):",
            disable_web_page_preview=True
        )
        
        # Wait for repo URL from user
        repo_msg = await client.listen(message.chat.id, timeout=120)
        repo_url = repo_msg.text.strip()
        
        # Extract repo slug
        try:
            if "github.com/" not in repo_url:
                raise ValueError("Invalid GitHub URL")
            repo_slug = repo_url.split("github.com/")[1]
            if repo_slug.endswith('.git'):
                repo_slug = repo_slug[:-4]
        except (IndexError, ValueError):
            await message.reply_text("❌ Invalid repo URL. Please provide a valid GitHub repository URL.")
            return
            
        await message.reply_text(
            "🔄 <b>Syncing your repo with upstream...</b> Please wait.",
            disable_web_page_preview=True
        )
        
        # Git operations
        commands = [
            # Remove current .git if exists (clean start)
            "rm -rf .git",
            
            # Re-init git and set your repo as origin
            "git init",
            f"git remote add origin https://{token}@github.com/{repo_slug}.git",
            "git remote add upstream https://github.com/NoxxOP/ShrutiMusic.git",
            
            # Configure git user (required for some operations)
            "git config user.name 'Nand Yaduwanshi'",
            "git config user.email 'badboy809075@gmail.com'",
            
            # Fetch and force reset to upstream
            "git fetch upstream",
            "git checkout -b main",
            "git reset --hard upstream/main",
            
            # Add all files and commit with custom message
            "git add -A",
            "git commit -m 'ᴛᴇʟᴇɢʀᴀᴍ @Sʜʀᴜᴛᴜʙᴏᴛs' --allow-empty",
            
            # Force push to user's repo
            "git push origin main --force"
        ]
        
        for cmd in commands:
            try:
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    await message.reply_text(
                        f"❌ <b>Error during update:</b>\n<code>{error_msg}</code>",
                        disable_web_page_preview=True
                    )
                    return
                    
            except Exception as e:
                await message.reply_text(
                    f"❌ <b>Command failed:</b> {cmd}\n<code>{str(e)}</code>",
                    disable_web_page_preview=True
                )
                return
        
        await message.reply_text(
            "✅ <b>Your repo has been fully synced with the main repo.</b>\n\n"
            "🔗 Now it's identical to: https://github.com/NoxxOP/ShrutiMusic",
            disable_web_page_preview=True
        )
        
    except asyncio.TimeoutError:
        await message.reply_text(
            "⏰ <b>Timeout!</b> Please try again and send the required information within 2 minutes.",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(
            f"❌ <b>Unexpected error:</b>\n<code>{str(e)}</code>",
            disable_web_page_preview=True
        )
