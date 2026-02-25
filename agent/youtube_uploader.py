"""
YouTube Uploader — uploads videos to your YouTube channel with
SEO-optimized metadata and custom thumbnails.

Optimized for international reach: US, UK, Europe, India.
"""

import logging
import os
import time
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# YouTube API scopes (must match auth_setup.py)
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

# Retry config for resumable uploads
MAX_RETRIES = 3
RETRY_DELAY = 5

# Subscribe CTA appended to every video description
SUBSCRIBE_FOOTER = (
    "\n\n" + "🔥" * 20 + "\n"
    "🔔 SUBSCRIBE NOW & hit the BELL for DAILY cartoon content!\n"
    "👇 Do you agree with this video?! Let us know in the COMMENTS!\n"
    "👍 LIKE this video to help us grow!\n"
    "📢 SHARE this with your friends who love cartoons!\n"
    + "🔥" * 20
)


def _get_youtube_service(token_file: str):
    """Create YouTube API service using OAuth2 credentials."""
    if not os.path.exists(token_file):
        logger.error(
            "token.json not found! Run 'python auth_setup.py' first "
            "to authorize YouTube access."
        )
        return None

    creds = Credentials.from_authorized_user_file(token_file)

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def _get_valid_tags(tags, max_chars=500):
    valid_tags = []
    current_length = 0
    for tag in tags:
        tag_len = len(tag)
        if current_length + tag_len <= max_chars:
            valid_tags.append(tag)
            current_length += tag_len + 1  # approximate +1 for separator if YouTube counts it
        else:
            break
    return valid_tags

def upload_video(
    token_file: str,
    file_path: str,
    title: str,
    description: str,
    tags: list,
    thumbnail_path: Optional[str] = None,
    privacy: str = "public",
    category_id: str = "24",  # Entertainment
    **kwargs,
) -> Optional[str]:
    """
    Upload a video to YouTube with metadata and optional custom thumbnail.

    Args:
        token_file: Path to OAuth2 token file
        file_path: Path to the video file
        title: Video title
        description: Video description
        tags: List of tags
        thumbnail_path: Path to custom thumbnail image (optional)
        privacy: "public", "unlisted", or "private"
        category_id: YouTube category ID (1 = Film & Animation)

    Returns:
        YouTube video URL, or None on failure
    """
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Video file not found: {file_path}")
        return None

    service = _get_youtube_service(token_file)
    if not service:
        return None

    # Append subscribe footer to description (if not already present)
    full_description = description
    if "SUBSCRIBE" not in description:
        full_description = description + SUBSCRIBE_FOOTER

    body = {
        "snippet": {
            "title": title[:100],
            "description": full_description[:5000],
            "tags": _get_valid_tags(tags, 400) if tags else [],  # safe buffer 400
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    
    # Algorithmic Hijacking: Global Polyglot
    # If the localizations dict was passed in via kwargs/video object, attach it to the API request
    localizations = kwargs.get("localizations")
    if localizations:
        body["localizations"] = localizations

    media = MediaFileUpload(
        file_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024,  # 1 MB chunks
    )

    try:
        # If localizations are in the body, they must be in the 'part' parameter too
        part = "snippet,status"
        if "localizations" in body:
            part += ",localizations"

        # Upload video
        request = service.videos().insert(
            part=part,
            body=body,
            media_body=media,
        )

        video_id = _resumable_upload(request)
        if not video_id:
            return None

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"✅ Uploaded to YouTube: {title} → {video_url}")

        # Set custom thumbnail if provided
        if thumbnail_path and os.path.exists(thumbnail_path):
            _set_thumbnail(service, video_id, thumbnail_path)

        # Post the engagement trap comment
        _post_engagement_comment(service, video_id)

        return video_url

    except HttpError as e:
        logger.error(f"❌ YouTube upload failed for '{title}': {e}")
        return None
    except Exception as e:
        logger.error(f"❌ YouTube upload error for '{title}': {e}")
        return None


def _resumable_upload(request) -> Optional[str]:
    """Execute a resumable upload with retries."""
    response = None
    retry = 0

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"  ↑ Upload progress: {progress}%")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504] and retry < MAX_RETRIES:
                retry += 1
                wait = RETRY_DELAY * retry
                logger.warning(f"  ⚠️ Server error, retrying in {wait}s... ({retry}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                raise

    return response.get("id") if response else None


def _set_thumbnail(service, video_id: str, thumbnail_path: str):
    """Set a custom thumbnail for an uploaded video."""
    try:
        media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
        service.thumbnails().set(
            videoId=video_id,
            media_body=media,
        ).execute()
        logger.info(f"🎨 Custom thumbnail set for video {video_id}")
    except HttpError as e:
        # Custom thumbnails require a verified YouTube account
        if "forbidden" in str(e).lower():
            logger.warning(
                "⚠️ Could not set thumbnail — your YouTube account may need "
                "phone verification to use custom thumbnails. "
                "Go to https://www.youtube.com/verify"
            )
        else:
            logger.warning(f"⚠️ Could not set thumbnail: {e}")


def _post_engagement_comment(service, video_id: str):
    """Post a polarizing, high-engagement 'trap' comment on the newly uploaded video."""
    import random
    
    # Highly polarizing and engaging questions to force viewer interaction
    BAIT_COMMENTS = [
        "Unpopular opinion: this is actually the best scene of all time. Prove me wrong 👇",
        "Who else agrees with what happened at the end?! Let me know below! 👇👇",
        "I bet 99% of people missed the hidden detail at 0:15... Did you see it? 👀",
        "If you remember watching this on TV, your childhood was awesome. Drop a 🔥 if you agree!",
        "This still makes me laugh way harder than it should 😂 What's your favorite part?",
        "Do you think they went too far with this joke? Let the debate begin 👇",
        "Only true fans know the backstory behind this scene... Prove you're a real one in the comments 👀"
    ]
    
    comment_text = random.choice(BAIT_COMMENTS)
    
    try:
        # Create a top-level comment string
        body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
        
        service.commentThreads().insert(
            part="snippet",
            body=body
        ).execute()
        logger.info(f"🪤 Engagement trap comment posted: '{comment_text}'")
        
        # Note: We cannot automatically pin the comment via the API as of 2026, 
        # but posting it as the channel owner still pins it to the top of the feed visually.
        
    except HttpError as e:
        logger.warning(f"⚠️ Could not post engagement comment: {e}")


def upload_videos_to_youtube(
    token_file: str,
    videos: list,
    privacy: str = "public",
) -> list:
    """
    Upload multiple videos to YouTube.

    Each video dict should have: file_path, seo_title, seo_description,
    seo_tags, thumbnail_path

    Returns the video list with 'youtube_url' added to each.
    """
    results = []
    for video in videos:
        file_path = video.get("file_path")
        title = video.get("seo_title", video.get("title", "Untitled"))
        description = video.get("seo_description", "")
        tags = video.get("seo_tags", [])
        thumbnail_path = video.get("thumbnail_path")

        youtube_url = None
        if file_path and os.path.exists(file_path):
            youtube_url = upload_video(
                token_file=token_file,
                file_path=file_path,
                title=title,
                description=description,
                tags=tags,
                thumbnail_path=thumbnail_path,
                privacy=privacy,
                localizations=video.get("localizations")
            )

        video_with_url = dict(video)
        video_with_url["youtube_url"] = youtube_url
        results.append(video_with_url)

    uploaded = sum(1 for v in results if v.get("youtube_url"))
    logger.info(f"Uploaded {uploaded}/{len(videos)} videos to YouTube")
    return results
