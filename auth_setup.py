"""
One-time Google authorization — run this to generate token.json.

Usage: python auth_setup.py

This will open your browser to authorize access to:
  - Google Drive (upload videos)
  - YouTube (upload to your channel, set thumbnails)

The resulting token is saved as token.json and used by the agent.
"""

import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")


def main():
    """Run the OAuth2 authorization flow."""
    creds = None

    # Check for existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if creds and creds.valid:
            print("✅ Already authorized! token.json is valid.")
            return
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token expired, refreshing...")
            creds.refresh(Request())
            _save_token(creds)
            print("✅ Token refreshed successfully!")
            return

    # Check for credentials.json
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ credentials.json not found!")
        print()
        print("To create it:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Select your 'cartoon-shorts-agent' project")
        print("3. Go to APIs & Services → Credentials")
        print("4. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'")
        print("5. Application type: 'Desktop app', Name: 'Cartoon Agent'")
        print("6. Click 'Create'")
        print("7. Click 'DOWNLOAD JSON' and save as 'credentials.json'")
        print("   in the project folder (e:\\Antigravity\\)")
        return

    # Delete old token to force re-auth with new scopes
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("🔄 Removed old token to re-authorize with new scopes...")

    # Run authorization flow
    print("🔑 Opening browser for Google Drive + YouTube authorization...")
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    print("✅ Authorization successful! token.json saved.")
    print("   The agent can now upload videos to Drive and YouTube.")


def _save_token(creds):
    """Save credentials to token.json."""
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


if __name__ == "__main__":
    main()
