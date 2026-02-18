# 🎬 Cartoon Shorts Agent

An automated AI agent that discovers **trending cartoon YouTube Shorts** and posts them to your **Telegram channel** — hosted **100% free** via GitHub Actions.

## ✨ Features

- 🔍 **Smart Discovery** — Searches YouTube across multiple queries for maximum coverage
- 📊 **Trending Ranker** — Scores videos by views, engagement ratio, and recency
- 🚫 **No Duplicates** — Tracks posted videos to never repeat content
- 🤖 **Fully Automated** — Runs every 6 hours via GitHub Actions (free!)
- 💰 **Zero Cost** — No paid APIs, no servers, no subscriptions

## 🚀 Quick Start

### 1. Get Your API Keys (all free)

| Key | Where to Get |
|-----|-------------|
| YouTube Data API v3 | [Google Cloud Console](https://console.cloud.google.com) |
| Telegram Bot Token | [@BotFather](https://t.me/BotFather) on Telegram |
| Channel ID | Your channel's `@username` |

> 📖 **Detailed instructions**: See [setup_guide.md](setup_guide.md)

### 2. Set Up the Repository

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/cartoon-shorts-agent.git
cd cartoon-shorts-agent

# Install dependencies (for local testing)
pip install -r requirements.txt

# Copy and fill in your env vars
cp .env.example .env
# Edit .env with your API keys
```

### 3. Test Locally

```bash
# Dry run (fetches & ranks but doesn't post)
python main.py --dry-run

# Full run (posts to Telegram)
python main.py
```

### 4. Deploy to GitHub (Free Hosting)

1. Push code to a GitHub repository
2. Go to **Settings → Secrets → Actions** and add:
   - `YOUTUBE_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHANNEL_ID`
3. The agent runs automatically every 6 hours! 🎉

## 📁 Project Structure

```
├── agent/
│   ├── youtube_fetcher.py    # YouTube API integration
│   ├── ranker.py             # Trending score algorithm
│   ├── telegram_poster.py    # Telegram channel posting
│   └── dedup.py              # Duplicate prevention
├── main.py                   # Orchestrator
├── config.py                 # Environment-based config
├── .github/workflows/        # GitHub Actions cron job
└── posted_videos.json        # Auto-generated tracker
```

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_POSTS_PER_RUN` | 3 | Videos posted each run |
| `MAX_VIDEO_AGE_HOURS` | 48 | Only fetch videos newer than this |

## 🧠 How the Ranking Works

Each video gets a score from 0–1:

| Signal | Weight | What It Measures |
|--------|--------|-----------------|
| Views | 40% | Raw popularity |
| Engagement | 30% | Likes-to-views ratio (quality) |
| Recency | 30% | How recently it was published |

## 📄 License

MIT — Free to use and modify.
