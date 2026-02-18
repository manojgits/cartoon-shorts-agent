"""
Telegram Poster — sends trending cartoon video links to your Telegram DM.
"""

import asyncio
import logging

from telegram import Bot
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


def _format_view_count(count: int) -> str:
    """Format large numbers nicely (e.g., 1.2M, 45.3K)."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def _format_duration(seconds: int) -> str:
    """Format seconds to MM:SS or H:MM:SS."""
    if seconds <= 0:
        return "N/A"
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _build_message(video: dict, index: int) -> str:
    """
    Build a rich Telegram message for a single video.
    """
    title = video.get("title", "Untitled")
    channel = video.get("channel_title", "Unknown")
    views = _format_view_count(video.get("views", 0))
    likes = _format_view_count(video.get("likes", 0))
    video_id = video.get("video_id", "")
    score = video.get("score", 0)
    duration = _format_duration(video.get("duration_seconds", 0))
    url = f"https://www.youtube.com/watch?v={video_id}"
    drive_link = video.get("drive_link", "")

    # Determine type label
    is_short = video.get("duration_seconds", 0) <= 60
    type_label = "⚡ Short" if is_short else "🎥 Full Video"

    message = (
        f"🎬 <b>Trending Cartoon #{index}</b> ({type_label})\n"
        f"\n"
        f"📌 <b>{title}</b>\n"
        f"📺 {channel}\n"
        f"⏱ Duration: {duration}\n"
        f"\n"
        f"👁 Views: <b>{views}</b>  |  ❤️ Likes: <b>{likes}</b>\n"
        f"⭐ Trend Score: <b>{score:.2f}</b>\n"
        f"\n"
        f"🔗 <a href=\"{url}\">Watch on YouTube</a>\n"
    )

    if drive_link:
        message += f"📥 <a href=\"{drive_link}\">Download from Google Drive</a>\n"

    message += (
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <i>Found by Cartoon Agent</i>"
    )
    return message


async def _send_video_message(bot: Bot, chat_id: str, video: dict, index: int):
    """Send a single video as a message to the user's Telegram DM."""
    message = _build_message(video, index)
    thumbnail_url = video.get("thumbnail_url", "")

    try:
        if thumbnail_url:
            # Send as a photo with caption
            await bot.send_photo(
                chat_id=chat_id,
                photo=thumbnail_url,
                caption=message,
                parse_mode=ParseMode.HTML,
            )
        else:
            # Fallback: send as text only
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
        logger.info(f"✅ Posted: {video.get('title', 'Untitled')}")
    except Exception as e:
        logger.error(f"❌ Failed to post '{video.get('title', '')}': {e}")


async def _post_all(bot_token: str, chat_id: str, videos: list):
    """Async function to post all videos to the user's Telegram DM."""
    bot = Bot(token=bot_token)

    # Send a header message if we have videos
    if videos:
        header = (
            "🔥 <b>Trending Cartoons Alert!</b> 🔥\n"
            f"\n"
            f"Found <b>{len(videos)}</b> trending cartoon videos for you!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=header,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(f"Failed to send header message: {e}")

    # Post each video with a small delay to avoid rate limits
    for i, video in enumerate(videos, start=1):
        await _send_video_message(bot, chat_id, video, i)
        if i < len(videos):
            await asyncio.sleep(1.5)  # Respect Telegram rate limits


def post_to_telegram(bot_token: str, chat_id: str, videos: list):
    """
    Post a list of videos to the user's Telegram DM.
    This is the synchronous entry point that runs the async posting internally.
    """
    if not videos:
        logger.info("No videos to post.")
        return

    logger.info(f"Sending {len(videos)} videos to Telegram chat: {chat_id}")

    # Use a custom event loop to avoid Python 3.9 Windows
    # "RuntimeError: Event loop is closed" bug with ProactorEventLoop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_post_all(bot_token, chat_id, videos))
    finally:
        loop.close()

    logger.info("Finished sending to Telegram.")
