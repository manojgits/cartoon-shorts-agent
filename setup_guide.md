# 📖 Setup Guide — Cartoon Shorts Agent

This guide walks you through getting all three free API keys and deploying the agent on GitHub Actions.

---

## Step 1: Create a YouTube Data API Key (Free)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **New Project** → Name it `cartoon-shorts-agent` → **Create**
3. In the left sidebar, go to **APIs & Services → Library**
4. Search for **YouTube Data API v3** → Click it → Click **Enable**
5. Go to **APIs & Services → Credentials**
6. Click **+ CREATE CREDENTIALS** → **API Key**
7. Copy the API key — this is your `YOUTUBE_API_KEY`

> **💡 Tip:** Click "Edit API key" and restrict it to only "YouTube Data API v3" for security.

### Free Quota
- You get **10,000 units per day** for free
- Each agent run uses ~200-400 units
- Running 4 times/day = ~1,600 units (well within limits)

---

## Step 2: Create a Telegram Bot (Free)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., `Cartoon Shorts Bot`)
4. Choose a username (e.g., `cartoon_shorts_agent_bot`) — must end in `bot`
5. BotFather will reply with your **bot token** — copy it, this is your `TELEGRAM_BOT_TOKEN`

> **⚠️ Keep this token secret!** Anyone with it can control your bot.

---

## Step 3: Set Up Your Telegram Channel

### Create the Channel (if you don't have one)
1. Open Telegram → Hamburger menu (☰) → **New Channel**
2. Name it (e.g., `Trending Cartoon Shorts`)
3. Make it **Public** and set a username (e.g., `@cartoon_shorts_trending`)

### Add the Bot as Admin
1. Open your channel → Click the channel name → **Administrators**
2. Click **Add Administrator**
3. Search for your bot by its username
4. Grant it **Post Messages** permission → **Save**

### Get Your Channel ID
- If public: Your channel ID is `@your_channel_username` (e.g., `@cartoon_shorts_trending`)
- If private: Forward a message from your channel to `@userinfobot` to get the numeric ID (e.g., `-1001234567890`)

This is your `TELEGRAM_CHANNEL_ID`.

---

## Step 4: Test Locally

```bash
# 1. Install Python 3.11+ if you don't have it
python --version

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env

# 4. Edit .env and paste your keys:
#    YOUTUBE_API_KEY=AIza...
#    TELEGRAM_BOT_TOKEN=7123456789:AAF...
#    TELEGRAM_CHANNEL_ID=@your_channel_name

# 5. Test with a dry run (no posting)
python main.py --dry-run

# 6. Full run (will post to your channel!)
python main.py
```

---

## Step 5: Deploy to GitHub Actions (Free Hosting)

### Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Cartoon Shorts Agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cartoon-shorts-agent.git
git push -u origin main
```

### Add Secrets
1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add each:

| Secret Name | Value |
|------------|-------|
| `YOUTUBE_API_KEY` | Your YouTube API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHANNEL_ID` | `@your_channel_name` or numeric ID |

### Enable GitHub Actions
1. Go to the **Actions** tab in your repo
2. You should see the "Run Cartoon Shorts Agent" workflow
3. Click **Run workflow** → **Run workflow** to test it manually
4. Check your Telegram channel — you should see posts! 🎉

### Schedule
The agent runs automatically every 6 hours (`0 */6 * * *`). You can change this in `.github/workflows/run_agent.yml`.

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing required environment variables" | Make sure all 3 secrets are set in GitHub settings |
| No videos found | Try wider search queries in `config.py` or increase `MAX_VIDEO_AGE_HOURS` |
| Bot can't post to channel | Ensure the bot is added as a channel admin with post permissions |
| GitHub Actions not running | Go to Actions tab → check the workflow is enabled |
| YouTube API quota exceeded | Reduce run frequency or number of search queries |

---

## 💡 Customization

### Change Search Queries
Edit the `SEARCH_QUERIES` list in `config.py` to target different cartoon niches:

```python
SEARCH_QUERIES = [
    "anime shorts trending",
    "3D animation shorts",
    "cartoon edit shorts",
    # Add your own!
]
```

### Change Posting Frequency
Edit the cron schedule in `.github/workflows/run_agent.yml`:

```yaml
schedule:
  - cron: '0 */12 * * *'  # Every 12 hours
  - cron: '0 8,20 * * *'  # Twice a day at 8am and 8pm UTC
```

### Post More/Fewer Videos
Set `MAX_POSTS_PER_RUN` in your environment variables or directly in `config.py`.
