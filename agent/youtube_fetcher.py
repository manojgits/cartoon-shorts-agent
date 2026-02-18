"""
YouTube Fetcher — finds trending cartoon videos using YouTube Data API v3.
"""

import logging
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def _build_youtube_client(api_key: str):
    """Create a YouTube API client."""
    return build("youtube", "v3", developerKey=api_key)


def _get_published_after(max_age_hours: int) -> str:
    """Return an RFC 3339 timestamp for `max_age_hours` ago."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")


def search_videos(api_key: str, query: str, max_age_hours: int = 48, max_results: int = 15):
    """
    Search YouTube for recent trending cartoon videos matching a query.

    Returns a list of video IDs from the search.
    """
    youtube = _build_youtube_client(api_key)
    published_after = _get_published_after(max_age_hours)

    try:
        response = youtube.search().list(
            part="id,snippet",
            q=query,
            type="video",
            order="viewCount",           # Sort by popularity
            publishedAfter=published_after,
            maxResults=max_results,
            relevanceLanguage="en",
        ).execute()
    except HttpError as e:
        logger.error(f"YouTube API search error: {e}")
        return []

    video_ids = []
    for item in response.get("items", []):
        vid_id = item["id"].get("videoId")
        if vid_id:
            video_ids.append(vid_id)

    return video_ids


def get_video_details(api_key: str, video_ids: list) -> list:
    """
    Fetch detailed stats for a list of video IDs.

    Returns a list of dicts with: video_id, title, channel_title,
    views, likes, published_at, thumbnail_url, duration_seconds.
    """
    if not video_ids:
        return []

    youtube = _build_youtube_client(api_key)

    try:
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids),
        ).execute()
    except HttpError as e:
        logger.error(f"YouTube API video details error: {e}")
        return []

    videos = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})

        # Parse ISO 8601 duration (PT#M#S) to seconds
        duration_str = content.get("duration", "PT0S")
        duration_sec = _parse_duration(duration_str)

        videos.append({
            "video_id": item["id"],
            "title": snippet.get("title", "Untitled"),
            "channel_title": snippet.get("channelTitle", "Unknown"),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "duration_seconds": duration_sec,
        })

    logger.info(f"Fetched details for {len(videos)} videos from {len(video_ids)} candidates")
    return videos


def _parse_duration(duration_str: str) -> int:
    """
    Parse an ISO 8601 duration string (e.g. 'PT1M30S', 'PT45S') to seconds.
    """
    import re
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def fetch_trending_cartoons(api_key: str, queries: list, max_age_hours: int = 48) -> list:
    """
    Main entry point: search multiple queries and return combined video details.

    This fetches from multiple search queries to get a diverse set of cartoon videos,
    then fetches detailed stats for all of them.
    """
    all_video_ids = []
    seen_ids = set()

    for query in queries:
        logger.info(f"Searching YouTube for: '{query}'")
        ids = search_videos(api_key, query, max_age_hours=max_age_hours, max_results=10)
        for vid_id in ids:
            if vid_id not in seen_ids:
                seen_ids.add(vid_id)
                all_video_ids.append(vid_id)

    logger.info(f"Found {len(all_video_ids)} unique video IDs across {len(queries)} queries")

    # Fetch details in batches of 50 (API limit)
    all_videos = []
    for i in range(0, len(all_video_ids), 50):
        batch = all_video_ids[i:i + 50]
        details = get_video_details(api_key, batch)
        all_videos.extend(details)

    return all_videos
