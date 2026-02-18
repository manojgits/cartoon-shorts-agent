"""
Ranker — scores and ranks cartoon shorts by trending signals.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _recency_score(published_at: str, max_age_hours: int = 48) -> float:
    """
    Score from 0.0 to 1.0 based on how recent the video is.
    A video published just now scores 1.0; one at max_age_hours scores 0.0.
    """
    if not published_at:
        return 0.0

    try:
        pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age_hours = (now - pub_time).total_seconds() / 3600

        if age_hours <= 0:
            return 1.0
        if age_hours >= max_age_hours:
            return 0.0

        return 1.0 - (age_hours / max_age_hours)
    except (ValueError, TypeError):
        return 0.0


def _engagement_score(views: int, likes: int) -> float:
    """
    Score based on likes-to-views ratio (engagement quality).
    Returns 0.0 to 1.0. A 10%+ like ratio is considered excellent.
    """
    if views <= 0:
        return 0.0

    ratio = likes / views
    # Cap at 0.15 (15% like ratio is exceptional)
    return min(ratio / 0.15, 1.0)


def _views_score(views: int, max_views: int) -> float:
    """
    Normalize views to 0.0–1.0 relative to the max views in the batch.
    """
    if max_views <= 0:
        return 0.0
    return min(views / max_views, 1.0)


def rank_videos(videos: list, max_age_hours: int = 48) -> list:
    """
    Score and rank videos using a weighted formula:
      - Views weight:      0.40 (popularity signal)
      - Engagement weight:  0.30 (quality signal — likes/views ratio)
      - Recency weight:     0.30 (freshness signal)

    Returns videos sorted by score (highest first), with a 'score' field added.
    """
    if not videos:
        return []

    # Find the max views for normalization
    max_views = max(v.get("views", 0) for v in videos)

    scored = []
    for video in videos:
        views = video.get("views", 0)
        likes = video.get("likes", 0)
        published_at = video.get("published_at", "")

        v_score = _views_score(views, max_views)
        e_score = _engagement_score(views, likes)
        r_score = _recency_score(published_at, max_age_hours)

        total_score = (0.40 * v_score) + (0.30 * e_score) + (0.30 * r_score)

        video_copy = dict(video)
        video_copy["score"] = round(total_score, 4)
        video_copy["score_breakdown"] = {
            "views": round(v_score, 3),
            "engagement": round(e_score, 3),
            "recency": round(r_score, 3),
        }
        scored.append(video_copy)

    scored.sort(key=lambda v: v["score"], reverse=True)

    logger.info(f"Ranked {len(scored)} videos. Top score: {scored[0]['score'] if scored else 'N/A'}")
    return scored


def get_top_videos(videos: list, posted_ids: set, max_count: int = 3, max_age_hours: int = 48) -> list:
    """
    Rank videos and return the top N that haven't been posted yet.
    """
    ranked = rank_videos(videos, max_age_hours)

    top = []
    for video in ranked:
        if video["video_id"] not in posted_ids:
            top.append(video)
            if len(top) >= max_count:
                break

    logger.info(f"Selected {len(top)} new videos to post (skipped {len(posted_ids)} already-posted)")
    return top
