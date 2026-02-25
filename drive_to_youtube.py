"""
Drive to YouTube Recovery Script
Downloads videos from the Google Drive folder and uploads them to YouTube.
Use this to retry uploads that failed during the main run.
"""

import os
import io
import logging
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import config
from agent.gemini_seo import generate_seo
from agent.youtube_uploader import upload_video

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("recovery")

def get_service(name, version):
    creds = Credentials.from_authorized_user_file(config.TOKEN_FILE)
    return build(name, version, credentials=creds)

def download_from_drive(service, file_id, filename):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        logger.info(f"Download Progress: {int(status.progress() * 100)}%")
    return filename

def run_recovery():
    drive = get_service('drive', 'v3')
    folder_id = config.GOOGLE_DRIVE_FOLDER_ID
    
    if not folder_id:
        logger.error("GOOGLE_DRIVE_FOLDER_ID not set in .env")
        return

    logger.info(f"Listing files in Drive folder: {folder_id}...")
    results = drive.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, createdTime)",
        orderBy="createdTime desc",
        pageSize=5
    ).execute()
    
    files = results.get('files', [])
    if not files:
        logger.info("No files found in Drive folder.")
        return

    os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)

    for file in files:
        file_id = file['id']
        file_name = file['name']
        
        # We assume the filename contains the title, e.g. "Title [VideoID].mp4"
        # We'll just use the filename base as the title for SEO
        clean_name = file_name.rsplit('.', 1)[0]
        logger.info(f"Processing: {clean_name} ({file_id})")
        
        # Download
        local_path = os.path.join(config.DOWNLOADS_DIR, file_name)
        if not os.path.exists(local_path):
            logger.info(f"Downloading {file_name}...")
            download_from_drive(drive, file_id, local_path)
        
        # Generate SEO
        logger.info(f"Generating SEO for: {clean_name}")
        seo = generate_seo(config.GEMINI_API_KEY, clean_name, "Short")
        
        if not seo:
            logger.warning("SEO generation failed, skipping or use fallback.")
            continue

        # Upload to YouTube
        logger.info(f"Uploading to YouTube: {seo['title']}")
        youtube_url = upload_video(
            token_file=config.TOKEN_FILE,
            file_path=local_path,
            title=seo["title"],
            description=seo["description"],
            tags=seo["tags"],
            localizations=seo.get("localizations"),
            privacy=config.YOUTUBE_PRIVACY
        )
        
        if youtube_url:
            logger.info(f"🎉 SUCCESS: {youtube_url}")
        else:
            logger.error(f"❌ Failed to upload {file_name} to YouTube.")

if __name__ == "__main__":
    run_recovery()
