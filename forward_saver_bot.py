import asyncio
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from telethon import TelegramClient, events
from yt_dlp import YoutubeDL


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# VALIDATE CONFIG
# ============================================================

if not API_ID:
    raise RuntimeError("API_ID is missing from .env")

if not API_HASH:
    raise RuntimeError("API_HASH is missing from .env")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing from .env")

try:
    API_ID = int(API_ID)
except ValueError:
    raise RuntimeError("API_ID must be a number")


# ============================================================
# TELEGRAM CLIENT
# ============================================================

bot = TelegramClient(
    "forward_saver_bot",
    API_ID,
    API_HASH
)


# ============================================================
# URL HELPERS
# ============================================================

def is_valid_url(url: str) -> bool:
    """Check whether a string looks like a valid HTTP/HTTPS URL."""

    try:
        parsed = urlparse(url)

        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    except Exception:
        return False


def get_platform(url: str) -> str:
    """Identify the platform from a URL."""

    hostname = urlparse(url).netloc.lower()

    hostname = hostname.replace("www.", "")

    if "instagram.com" in hostname:
        return "Instagram"

    if "youtube.com" in hostname or "youtu.be" in hostname:
        return "YouTube"

    if "pinterest.com" in hostname or "pin.it" in hostname:
        return "Pinterest"

    if "twitter.com" in hostname or "x.com" in hostname:
        return "Twitter/X"

    return "Unknown"


# ============================================================
# DOWNLOAD FUNCTION
# ============================================================

def download_media_sync(url: str, output_dir: str) -> list[str]:
    """
    Download one public media URL using yt-dlp.

    This function is synchronous because yt-dlp itself is synchronous.
    It is executed in a background thread by download_media().
    """

    output_path = Path(output_dir)

    ydl_opts = {
        # Prefer a single video file when possible.
        "format": "bv*+ba/b",

        # Automatically merge audio/video when necessary.
        "merge_output_format": "mp4",

        # Save using a safe filename.
        "outtmpl": str(output_path / "%(id)s.%(ext)s"),

        # Do not download playlists.
        "noplaylist": True,

        # Avoid unnecessary console output.
        "quiet": True,
        "no_warnings": True,

        # Do not download subtitles/thumbnails unless required.
        "writesubtitles": False,
        "writethumbnail": False,

        # Continue partial downloads where possible.
        "continuedl": True,

        # Network retry settings.
        "retries": 3,
        "fragment_retries": 3,

        # Do not use browser cookies automatically.
        # Public URLs only.
    }

    downloaded_files: list[str] = []

    try:
        with YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            if not info:
                return []

            # yt-dlp can return an entry for some URLs.
            if "entries" in info:
                entries = [
                    entry for entry in info["entries"]
                    if entry
                ]
            else:
                entries = [info]

            # Find files created inside the temporary directory.
            for file_path in output_path.iterdir():

                if not file_path.is_file():
                    continue

                # Ignore temporary files.
                if file_path.name.endswith(".part"):
                    continue

                downloaded_files.append(str(file_path))

            # Remove duplicates while preserving order.
            downloaded_files = list(
                dict.fromkeys(downloaded_files)
            )

            return downloaded_files

    except Exception as error:
        print(f"Download error: {error}")
        return []


async def download_media(url: str) -> list[str]:
    """
    Run yt-dlp outside the main asyncio event loop.
    """

    temp_dir = tempfile.mkdtemp(
        prefix="forward_saver_",
        dir=DOWNLOAD_DIR
    )

    try:
        files = await asyncio.to_thread(
            download_media_sync,
            url,
            temp_dir
        )

        return files

    except Exception as error:
        print(f"Background download error: {error}")

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        return []


# ============================================================
# SEND MEDIA
# ============================================================

async def send_downloaded_files(
    event,
    files: list[str],
    caption: str
):
    """Send downloaded files back to the Telegram chat."""

    if not files:
        return

    for file_path in files:

        path = Path(file_path)

        if not path.exists():
            continue

        try:

            extension = path.suffix.lower()

            # Video files
            if extension in {
                ".mp4",
                ".mkv",
                ".webm",
                ".mov",
                ".avi"
            }:

                await event.client.send_file(
                    event.chat_id,
                    str(path),
                    caption=caption,
                    supports_streaming=True
                )

            # Image files
            elif extension in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
                ".gif"
            }:

                await event.client.send_file(
                    event.chat_id,
                    str(path),
                    caption=caption
                )

            # Everything else
            else:

                await event.client.send_file(
                    event.chat_id,
                    str(path),
                    caption=caption,
                    force_document=True
                )

        except Exception as error:

            print(
                f"Telegram upload failed "
                f"for {path.name}: {error}"
            )

            await event.reply(
                f"❌ Failed to send `{path.name}`\n"
                f"Reason: `{error}`"
            )

        finally:

            # Delete the file after processing.
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass

    # Remove the temporary directory.
    try:

        parent = Path(files[0]).parent

        if parent.exists():
            shutil.rmtree(
                parent,
                ignore_errors=True
            )

    except Exception:
        pass


# ============================================================
# COMMON DOWNLOAD HANDLER
# ============================================================

async def process_url(
    event,
    url: str,
    platform_name: str,
    emoji: str
):
    """Common logic used by all commands."""

    url = url.strip()

    if not is_valid_url(url):

        await event.reply(
            "❌ Invalid URL.\n\n"
            "Please send a complete HTTP/HTTPS URL."
        )

        return

    detected_platform = get_platform(url)

    if detected_platform == "Unknown":

        await event.reply(
            "❌ Unsupported URL.\n\n"
            "Supported platforms:\n"
            "• Instagram\n"
            "• Pinterest\n"
            "• YouTube\n"
            "• Twitter/X"
        )

        return

    status_message = await event.reply(
        f"{emoji} Downloading from {platform_name}...\n"
        "⏳ Please wait."
    )

    files = await download_media(url)

    if not files:

        try:
            await status_message.edit(
                f"❌ Failed to download from "
                f"{platform_name}.\n\n"
                "The URL may be private, unavailable, "
                "unsupported, or require authentication."
            )
        except Exception:
            await event.reply(
                f"❌ Failed to download from {platform_name}."
            )

        return

    try:
        await status_message.edit(
            f"✅ Download complete!\n"
            f"📤 Sending {len(files)} file(s)..."
        )
    except Exception:
        pass

    await send_downloaded_files(
        event,
        files,
        f"{emoji} {platform_name} Download"
    )

    try:
        await status_message.delete()
    except Exception:
        pass

# ============================================================
# AUTOMATIC URL DETECTION
# ============================================================

SUPPORTED_DOMAINS = (
    "instagram.com",
    "www.instagram.com",
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "pinterest.com",
    "www.pinterest.com",
    "pin.it",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
)


@bot.on(events.NewMessage)
async def automatic_url_handler(event):
    """
    Automatically detect supported URLs sent without a command.

    Examples:
        https://www.instagram.com/reel/...
        https://youtu.be/...
        https://pin.it/...
        https://x.com/...
    """

    # Ignore messages containing commands.
    text = event.raw_text.strip()

    if not text or text.startswith("/"):
        return

    # Find URLs in the message.
    urls = re.findall(
        r"https?://[^\s]+",
        text
    )

    if not urls:
        return

    for url in urls:

        # Remove common punctuation accidentally attached to URL.
        url = url.rstrip(".,!?)]}")

        hostname = urlparse(url).netloc.lower()

        if hostname not in SUPPORTED_DOMAINS:
            continue

        platform = get_platform(url)

        if platform == "Instagram":
            emoji = "📸"

        elif platform == "YouTube":
            emoji = "▶️"

        elif platform == "Pinterest":
            emoji = "📌"

        elif platform == "Twitter/X":
            emoji = "🐦"

        else:
            continue

        await process_url(
            event,
            url,
            platform,
            emoji
        )

        # Process only the first supported URL.
        break

# ============================================================
# /start
# ============================================================

@bot.on(events.NewMessage(pattern=r"^/start$"))
async def start_handler(event):

    await event.reply(
        "👋 **Forward Saver Bot**\n\n"
        "Send a public media URL using one of these commands:\n\n"
        "📸 `/insta <url>` — Instagram\n"
        "📌 `/pin <url>` — Pinterest\n"
        "▶️ `/yt <url>` — YouTube\n"
        "🐦 `/tw <url>` — Twitter/X\n\n"
        "Example:\n"
        "`/yt https://youtu.be/example`"
    )


# ============================================================
# /help
# ============================================================

@bot.on(events.NewMessage(pattern=r"^/help$"))
async def help_handler(event):

    await event.reply(
        "📖 **Commands**\n\n"
        "📸 `/insta <URL>`\n"
        "Download public Instagram media.\n\n"
        "📌 `/pin <URL>`\n"
        "Download public Pinterest media.\n\n"
        "▶️ `/yt <URL>`\n"
        "Download public YouTube media.\n\n"
        "🐦 `/tw <URL>`\n"
        "Download public Twitter/X media.\n\n"
        "⚠️ Private or restricted content that "
        "requires authentication is not supported."
    )


# ============================================================
# /insta
# ============================================================

@bot.on(events.NewMessage(pattern=r"^/insta\s+(.+)$"))
async def insta_handler(event):

    url = event.pattern_match.group(1).strip()

    await process_url(
        event,
        url,
        "Instagram",
        "📸"
    )


# ============================================================
# /pin
# ============================================================

@bot.on(events.NewMessage(pattern=r"^/pin\s+(.+)$"))
async def pin_handler(event):

    url = event.pattern_match.group(1).strip()

    await process_url(
        event,
        url,
        "Pinterest",
        "📌"
    )


# ============================================================
# /yt
# ============================================================

@bot.on(events.NewMessage(pattern=r"^/yt\s+(.+)$"))
async def yt_handler(event):

    url = event.pattern_match.group(1).strip()

    await process_url(
        event,
        url,
        "YouTube",
        "▶️"
    )


# ============================================================
# /tw
# ============================================================

@bot.on(events.NewMessage(pattern=r"^/tw\s+(.+)$"))
async def twitter_handler(event):

    url = event.pattern_match.group(1).strip()

    await process_url(
        event,
        url,
        "Twitter/X",
        "🐦"
    )


# ============================================================
# START BOT
# ============================================================

async def main():

    print("======================================")
    print("       Forward Saver Bot")
    print("======================================")
    print("Starting bot...")

    await bot.start(
        bot_token=BOT_TOKEN
    )

    me = await bot.get_me()

    print(
        f"Bot started: "
        f"@{me.username or me.first_name}"
    )

    print("Bot is running...")
    print("Press Ctrl+C to stop.")

    await bot.run_until_disconnected()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nBot stopped.")
