"""
Google Drive Uploader — uploads video files to Google Drive using a service account.
"""

import logging
import os
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_drive_service(service_account_file: str):
    """Create Google Drive API service using service account credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)


def upload_file(service_account_file: str, folder_id: str, file_path: str, title: str) -> Optional[str]:
    """
    Upload a single file to Google Drive.

    Returns the Google Drive file ID, or None on failure.
    """
    if not file_path or not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    try:
        service = _get_drive_service(service_account_file)

        file_metadata = {
            "name": f"{title}.mp4",
            "parents": [folder_id],
        }

        media = MediaFileUpload(
            file_path,
            mimetype="video/mp4",
            resumable=True,
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
        ).execute()

        drive_id = file.get("id")
        drive_link = file.get("webViewLink", "")
        logger.info(f"✅ Uploaded to Drive: {title} → {drive_link}")
        return drive_link

    except Exception as e:
        logger.error(f"❌ Failed to upload '{title}' to Drive: {e}")
        return None


def upload_videos(service_account_file: str, folder_id: str, videos: list) -> list:
    """
    Upload multiple videos to Google Drive.

    Returns the video list with 'drive_link' added to each.
    """
    results = []
    for video in videos:
        file_path = video.get("file_path")
        title = video.get("title", "Untitled")

        drive_link = None
        if file_path:
            drive_link = upload_file(service_account_file, folder_id, file_path, title)

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
