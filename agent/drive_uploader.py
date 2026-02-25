"""
Google Drive Uploader — uploads video files using OAuth2 user credentials.

Uses token.json (from auth_setup.py) to upload files with the user's own
Drive storage quota.
"""

import logging
import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_drive_service(token_file: str):
    """Create Google Drive API service using OAuth2 user credentials."""
    if not os.path.exists(token_file):
        logger.error(
            "token.json not found! Run 'python auth_setup.py' first "
            "to authorize Google Drive access."
        )
        return None

    creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def upload_file(token_file: str, folder_id: str, file_path: str, drive_name: str, mimetype: str = "video/mp4") -> Optional[str]:
    """
    Upload a single file to Google Drive.

    Returns the Google Drive web view link, or None on failure.
    """
    if not file_path or not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    service = _get_drive_service(token_file)
    if not service:
        return None

    try:
        file_metadata = {
            "name": drive_name,
            "parents": [folder_id],
        }

        media = MediaFileUpload(
            file_path,
            mimetype=mimetype,
            resumable=True,
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
        ).execute()

        drive_link = file.get("webViewLink", "")
        logger.info(f"✅ Uploaded to Drive: {drive_name} → {drive_link}")
        return drive_link

    except Exception as e:
        logger.error(f"❌ Failed to upload '{drive_name}' to Drive: {e}")
        return None


def upload_videos(token_file: str, folder_id: str, videos: list) -> list:
    """
    Upload multiple videos to Google Drive.

    Returns the video list with 'drive_link' added to each.
    """
    results = []
    for video in videos:
        file_path = video.get("file_path")
        title = video.get("title", "Untitled")
        seo_json_path = video.get("seo_json_path")

        drive_link = None
        if file_path:
            # 1. Upload the video file
            drive_link = upload_file(token_file, folder_id, file_path, f"{title}.mp4", "video/mp4")
            
            # 2. Upload SEO sidecar if it exists
            if seo_json_path and os.path.exists(seo_json_path):
                logger.info(f"📄 Uploading SEO sidecar to Drive for: {title}")
                upload_file(token_file, folder_id, seo_json_path, f"{title}_seo.json", "application/json")

        video_with_link = dict(video)
        video_with_link["drive_link"] = drive_link
        results.append(video_with_link)

    uploaded = sum(1 for v in results if v.get("drive_link"))
    logger.info(f"Uploaded {uploaded}/{len(videos)} videos to Google Drive")
    return results


def cleanup_downloads(download_dir: str):
    """Remove downloaded files to free up disk space."""
    if not os.path.exists(download_dir):
        return

    for filename in os.listdir(download_dir):
        filepath = os.path.join(download_dir, filename)
        try:
            os.remove(filepath)
            logger.info(f"🗑️ Cleaned up: {filename}")
        except OSError as e:
            logger.warning(f"Could not remove {filename}: {e}")
