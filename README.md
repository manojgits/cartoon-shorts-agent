# 🎬 Cartoon Shorts Viral Automation Agent

An automated, hyper-aggressive AI agent that discovers, downloads, and re-uploads **trending cartoon videos** to your YouTube channel. It leverages **Gemini 2.5 Flash** to automatically generate clickbait SEO, custom viral thumbnails, and deploys **algorithmic hijacking** strategies to force massive growth.

Runs fully autonomously twice a day (9:00 AM & 6:00 PM IST) for free via GitHub Actions.

## ✨ Core Features

- 🔍 **Smart Discovery** — Scrapes YouTube across US, UK, Europe, and India regions for viral Shorts.
- ⬇️ **Automated Downloading** — Downloads videos via `pytubefix` without watermarks.
- 🎨 **Gemini AI Thumbnails** — Uses Gemini to analyze the video and generate custom, high-CTR "MrBeast-style" viral thumbnails.
- 📝 **Gemini AI SEO** — Generates irresistible clickbait English titles, highly engaging descriptions, and trending tags.
- ☁️ **Google Drive Backup** — Uploads backups to Google Drive and sends Telegram notifications.
- 🚫 **Duplicate Prevention** — Tracks all posts to ensure you never re-upload the same video.
- 🤖 **Zero-Cost Automation** — Runs 100% autonomously in the cloud via GitHub Actions.

## 🚀 The Algorithmic Hijacking Suite (Aggressive Growth)

We have engineered this agent to forcefully manipulate the YouTube discovery algorithm using four aggressive strategies:

1. **The Engagement Trap (Auto-Commenting)**
   - Immediately after uploading, the agent uses your YouTube account to automatically post a highly polarizing question as the top comment (e.g., *"Unpopular opinion: this is actually the best scene. Prove me wrong 👇"*). This baits viewers into arguing, signaling massive engagement to the algorithm.

2. **The Keyword Bomber (Trend Hijacking)**
   - The agent artificially injects an invisible block of the day's biggest trending global search terms (e.g., *GTA 6, Taylor Swift, TikTok Viral*) at the very bottom of your video description to trick the search crawler.

3. **The Global Polyglot (Metadata Translation Spam)**
   - The agent uses Gemini to instantly translate your title and description into the 5 most spoken languages (*Spanish, Hindi, Arabic, Russian, Portuguese*). It submits all 5 directly to the YouTube API simultaneously, tricking the global crawler into pushing your video to international "For You" feeds.

4. **Competitor Leeching**
   - A hidden text string is generated in every description: `[Ignore: Viewers who watch MrBeast, Cocomelon, PewDiePie... will also love this]`. This exploits the "Up Next" AI crawler, forcing your Short into the recommended queue of massive 50-million subscriber channels.

## 🚀 Quick Start & Setup

### 1. Get Your API Keys (All Free)
| Key | Where to Get |
|-----|-------------|
| YouTube Data API v3 | [Google Cloud Console](https://console.cloud.google.com) |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| Telegram Bot Token | [@BotFather](https://t.me/BotFather) on Telegram |
| Chat/Channel ID | Your Telegram chat ID |
| Google Drive Folder | Create a folder in Drive → copy the ID from the URL |

### 2. Local Setup
```bash
git clone https://github.com/manojgits/cartoon-shorts-agent.git
cd cartoon-shorts-agent
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
*Fill in your `.env` file with all the API keys above.*

### 3. Generate YouTube OAuth Token (Crucial for Auto-Comments)
1. In Google Cloud, generate an **OAuth client ID (Desktop app)** and download it as `credentials.json` to the root folder.
2. Run `python auth_setup.py`.
3. Log in with your YouTube channel account. This creates a local `token.json` file.

### 4. Deploy to GitHub Actions (Free Hosting)
1. Push code to your GitHub repository.
2. Go to **Settings → Secrets and variables → Actions** and add these repository secrets:
    * `YOUTUBE_API_KEY`
    * `GEMINI_API_KEY`
    * `TELEGRAM_BOT_TOKEN`
    * `TELEGRAM_CHANNEL_ID`
    * `GOOGLE_DRIVE_FOLDER_ID`
    * `TOKEN` (Paste the exact contents of your newly generated `token.json` file here)
3. The agent runs automatically twice daily at **9:00 AM IST** and **6:00 PM IST** (Uploads 6 Shorts a day).

## ⚙️ Configuration (`config.py`)
| Variable | Default | Description |
|----------|---------|-------------|
| `NUM_SHORTS` | 3 | Number of Shorts to download/post per run (6 total daily) |
| `NUM_FULL_LENGTH` | 1 | Number of full-length videos per run |
| `MAX_VIDEO_AGE_HOURS` | 24 | Only fetch viral videos uploaded in the last 24 hours |

## 📄 License
MIT — Free to use and modify for absolute algorithmic domination.
