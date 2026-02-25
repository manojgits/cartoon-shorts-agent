"""
Video Downloader — downloads YouTube videos using pytubefix.
"""

import logging
import os
from typing import Optional
from pytubefix import YouTube

logger = logging.getLogger(__name__)


def _sanitize_filename(title: str) -> str:
    """Remove characters that are unsafe for filenames."""
    unsafe = '<>:"/\\|?*'
    for char in unsafe:
        title = title.replace(char, "")
    return title.strip()[:80]


def download_video(video_id: str, title: str, download_dir: str) -> Optional[str]:
    """
    Download a YouTube video using pytubefix.

    Returns the path to the downloaded file, or None if download fails.
    """
    os.makedirs(download_dir, exist_ok=True)
    safe_title = _sanitize_filename(title)
    filename = f"{safe_title} [{video_id}].mp4"
    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        # Use ANDROID client by default (proven to bypass bot detection in 10.3.8 without PO prompt)
        logger.info(f"📥 Attempting download with ANDROID client: {title}")
        yt = YouTube(url, client='ANDROID')
        stream = yt.streams.get_highest_resolution()

        if not stream:
            # Fallback to WEB_EMBED client
            logger.info(f"🔄 ANDROID client failed, trying WEB_EMBED client: {title}")
            yt = YouTube(url, client='WEB_EMBED')
            stream = yt.streams.get_highest_resolution()

        if not stream:
            logger.warning(f"⚠️ No stream found for: {title}")
            return None

        filepath = stream.download(output_path=download_dir, filename=filename)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"✅ Downloaded: {title} ({size_mb:.1f} MB)")
        return filepath

    except Exception as e:
        logger.warning(f"⚠️ Could not download '{title}': {e}")
        # Final fallback: try without any specific client
        try:
            logger.info(f"🔄 Final fallback attempt for: {title}")
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            if stream:
                filepath = stream.download(output_path=download_dir, filename=filename)
                return filepath
        except:
            pass
        return None


def download_videos(videos: list, download_dir: str) -> list:
    """
    Download multiple videos. Returns video list with 'file_path' added.
    Videos that fail to download will have file_path=None.
    """
    results = []
    for video in videos:
        filepath = download_video(
            video_id=video["video_id"],
            title=video["title"],
            download_dir=download_dir,
        )
        video_with_path = dict(video)
        video_with_path["file_path"] = filepath
        results.append(video_with_path)

    downloaded = sum(1 for v in results if v["file_path"])
    logger.info(f"Downloaded {downloaded}/{len(videos)} videos successfully")
    return results
