# 🎬 Cartoon Shorts Agent

An automated AI agent that discovers **trending cartoon videos** on YouTube — both **Shorts** and **full-length** — downloads them, uploads to **Google Drive**, and sends notifications with links to your **Telegram**. Runs daily for free via GitHub Actions.

## ✨ Features

- 🔍 **Smart Discovery** — Searches YouTube across multiple queries for Shorts (≤60s) and full-length (>60s) videos
- 📊 **Trending Ranker** — Scores videos by views, engagement ratio, and recency
- ⬇️ **Video Download** — Downloads videos using `pytubefix`
- ☁️ **Google Drive Upload** — Uploads downloaded videos with shareable links
- 💬 **Telegram Notifications** — Sends video thumbnail, info, YouTube link, and Drive download link
- 🚫 **No Duplicates** — Tracks posted videos to never repeat content
- 🤖 **Fully Automated** — Runs once daily at 9 AM IST via GitHub Actions (free!)
- 💰 **Zero Cost** — No paid APIs, no servers, no subscriptions

## 🚀 Quick Start

### 1. Get Your API Keys (all free)

| Key | Where to Get |
|-----|-------------|
| YouTube Data API v3 | [Google Cloud Console](https://console.cloud.google.com) |
| Telegram Bot Token | [@BotFather](https://t.me/BotFather) on Telegram |
| Chat/Channel ID | Your Telegram chat ID (use [@userinfobot](https://t.me/userinfobot)) |
| Google Drive Folder ID | Create a folder in Drive → copy the ID from the URL |

### 2. Set Up the Repository

```bash
# Clone the repo
git clone https://github.com/manojgits/cartoon-shorts-agent.git
cd cartoon-shorts-agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and fill in your env vars
cp .env.example .env
# Edit .env with your API keys
```

### 3. Set Up Google Drive (one-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com) → your project
2. Enable the **Google Drive API**
3. Go to **APIs & Services → Credentials**
4. Create **OAuth client ID** → **Desktop app**
5. Download the JSON → save as `credentials.json` in the project root
6. Set up the **OAuth consent screen**:
   - Choose **External** → add your email as a **test user**
7. Run the auth setup:

```bash
python auth_setup.py
```

This opens your browser to authorize Drive access. A `token.json` file is saved for future runs.

### 4. Test Locally

```bash
# Dry run — fetches & ranks but doesn't download/post
python main.py --dry-run

# Full run — downloads, uploads to Drive, and sends to Telegram
python main.py
```

### 5. Deploy to GitHub Actions (Free Hosting)

1. Push code to your GitHub repository
2. Go to **Settings → Secrets → Actions** and add:

| Secret | Value |
|--------|-------|
| `YOUTUBE_API_KEY` | Your YouTube Data API key |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHANNEL_ID` | Your Telegram chat ID |
| `GOOGLE_DRIVE_FOLDER_ID` | Your Drive folder ID |

3. The agent runs automatically once daily at **9:00 AM IST** 🎉

> **Note**: Google Drive upload on GitHub Actions requires additional setup (OAuth token as a secret). Without it, the agent still sends Telegram messages with YouTube links.

## 📁 Project Structure

```
├── agent/
│   ├── youtube_fetcher.py    # YouTube API — fetches Shorts & full-length
│   ├── ranker.py             # Trending score algorithm
│   ├── downloader.py         # Video download via pytubefix
│   ├── drive_uploader.py     # Google Drive upload via OAuth2
│   ├── telegram_poster.py    # Telegram notifications with links
│   └── dedup.py              # Duplicate prevention
├── main.py                   # Orchestrator
├── config.py                 # Environment-based config
├── auth_setup.py             # One-time Google Drive auth
├── .github/workflows/        # GitHub Actions daily cron job
├── requirements.txt          # Python dependencies
└── posted_videos.json        # Auto-generated tracker
```

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NUM_SHORTS` | 2 | Number of Shorts per run |
| `NUM_FULL_LENGTH` | 2 | Number of full-length videos per run |
| `MAX_VIDEO_AGE_HOURS` | 24 | Only fetch videos newer than this |

## 🧠 How the Ranking Works

Each video gets a score from 0–1:

| Signal | Weight | What It Measures |
|--------|--------|-----------------|
| Views | 40% | Raw popularity |
| Engagement | 30% | Likes-to-views ratio (quality) |
| Recency | 30% | How recently it was published |

## 🔧 Dependencies

- `google-api-python-client` — YouTube Data API
- `google-auth` + `google-auth-oauthlib` — Google Drive OAuth2
- `pytubefix` — YouTube video downloading
- `python-telegram-bot` — Telegram Bot API
- `python-dotenv` — Environment variable management

## 📄 License

MIT — Free to use and modify.
