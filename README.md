🥷 KageDrop

One link. One bot. Your media.

KageDrop is a Telegram media downloader bot that makes downloading publicly accessible media simple.

Instead of opening different websites or using separate downloaders, just send a supported URL to KageDrop. The bot automatically detects the platform, downloads the media, and sends it back to you directly in Telegram.

✨ What is KageDrop?

KageDrop is designed to provide a simple link → download → Telegram experience.

You don't need to type a command every time.

Just paste a supported URL:

https://www.instagram.com/reel/...

KageDrop detects that it's Instagram content, downloads it, and sends the media back to the chat.

The same workflow works with YouTube, Pinterest, and Twitter/X.

🌐 Supported Platforms

Platform

Status

📸 Instagram

✅

▶️ YouTube

✅

📌 Pinterest

✅

🐦 Twitter / X

✅

KageDrop is intended for publicly accessible content. Private, restricted, or authentication-required content may not be downloadable.

🚀 How to Use

1. Start the bot

Send:

/start

The bot will show the available features.

2. Paste a URL

Simply send a supported URL directly to the bot.

Example:

https://www.instagram.com/reel/example/

You don't need to type /insta.

KageDrop automatically detects the platform.

3. Wait for the download

The bot will show a status message while the media is being downloaded.

📸 Downloading from Instagram...
⏳ Please wait.

4. Receive your media

Once the download is complete, KageDrop uploads the media directly back to Telegram.

💬 Commands

Although automatic URL detection is the easiest way to use KageDrop, commands are also available.

/start

Displays the welcome message and basic instructions.

/help

Displays the available commands and supported platforms.

/insta <URL>

Download publicly accessible Instagram media.

/yt <URL>

Download publicly accessible YouTube media.

/pin <URL>

Download publicly accessible Pinterest media.

/tw <URL>

Download publicly accessible Twitter/X media.

⚡ Automatic URL Detection

This is the main feature of KageDrop.

You can simply paste a URL without using a command:

Instagram URL
       ↓
KageDrop detects Instagram
       ↓
Media is downloaded
       ↓
Media is sent to Telegram

The same process works for:

📸 Instagram

▶️ YouTube

📌 Pinterest

🐦 Twitter / X

This keeps the user experience fast and simple.

🛠️ Tech Stack

KageDrop is built with Python and uses:

🐍 Python — Core programming language

🤖 Telethon — Telegram client/API interaction

⬇️ yt-dlp — Media extraction and downloading

🔐 python-dotenv — Environment variable management

🎬 FFmpeg — Media processing and format handling

🐧 Linux VPS — 24/7 deployment

⚙️ systemd — Automatic bot management and restart

📦 Installation

Requirements

Python 3.10+

FFmpeg

Telegram API ID

Telegram API Hash

Telegram Bot Token

Linux VPS or local computer

Clone the repository

git clone https://github.com/archit-dot/kage-drop.git

cd kage-drop

Create a virtual environment

python3 -m venv venv

Activate it:

source venv/bin/activate

Install dependencies

pip install -r requirements.txt

🔐 Configuration

Create a .env file in the project directory:

API_ID=YOUR_API_ID

API_HASH=YOUR_API_HASH

BOT_TOKEN=YOUR_BOT_TOKEN

Never commit .env to GitHub.

Keep your Telegram API credentials and bot token private.

▶️ Run Locally

After configuring .env:

python forward_saver_bot.py

If configured correctly:

======================================
       Forward Saver Bot
======================================
Starting bot...
Bot started: @YourBot
Bot is running...
Press Ctrl+C to stop.

☁️ 24/7 VPS Deployment

KageDrop can run continuously on a Linux VPS using systemd.

Example service:

[Unit]
Description=KageDrop Telegram Media Downloader Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/kage-drop
ExecStart=/root/kage-drop/venv/bin/python /root/kage-drop/forward_saver_bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

Enable the service:

systemctl daemon-reload
systemctl enable kage-drop
systemctl start kage-drop

Check status:

systemctl status kage-drop

View live logs:

journalctl -u kage-drop -f

Restart:

systemctl restart kage-drop

Stop:

systemctl stop kage-drop

📁 Project Structure

kage-drop/
│
├── forward_saver_bot.py    # Main Telegram bot
├── requirements.txt        # Python dependencies
├── .env                    # Private configuration
├── .gitignore              # Ignored files
├── README.md               # Project documentation
│
├── downloads/              # Temporary downloaded media
│
└── venv/                   # Python virtual environment

.env, venv/, downloaded media, and Telegram session files should not be committed to GitHub.

🧹 Temporary Files

Downloaded media is stored temporarily while being processed.

After the media is sent to Telegram, temporary files are removed to reduce disk usage.

⚠️ Limitations

Downloads may fail when:

The URL is invalid

Content has been deleted

The account or post is private

Authentication is required

A platform blocks automated requests

The VPS/server IP is temporarily restricted

The media format is unsupported

A platform changes its website or download system

Regional or platform restrictions apply

KageDrop does not attempt to bypass private-content restrictions or authentication controls.

🔒 Privacy & Security

Downloaded files are processed temporarily and removed after processing.

Never publish:

API_ID
API_HASH
BOT_TOKEN
Telegram session files

If credentials are accidentally exposed, revoke or regenerate them immediately.

📜 Disclaimer

KageDrop is intended for legitimate and lawful use.

Users are responsible for ensuring that they have the necessary rights or permission to download and use the content they request.

Do not use KageDrop to infringe copyright, violate platform terms of service, or access content you are not authorized to access.

The project does not guarantee that every URL or platform will always be supported.

📄 License

This project is licensed under the MIT License.

See LICENSE for details.

⭐ Support the Project

If you find KageDrop useful:

⭐ Star the repository

🐛 Report bugs

💡 Suggest improvements

🔧 Contribute improvements

Every contribution helps improve the project.
