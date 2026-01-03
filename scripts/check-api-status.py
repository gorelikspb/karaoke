#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check if YouTube Data API v3 is enabled
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CREDENTIALS_FILE = "client_secrets.json"
TOKEN_FILE = "token.pickle"

print("Checking YouTube API status...")
print("=" * 50)

# Load credentials
if not os.path.exists(TOKEN_FILE):
    print("ERROR: No token found. Please authenticate first.")
    print("Run: python upload-to-youtube.py")
    exit(1)

with open(TOKEN_FILE, 'rb') as token:
    creds = pickle.load(token)

try:
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Try a simple API call
    print("Testing API access...")
    request = youtube.videos().list(part='snippet', myRating='none', maxResults=1)
    request.execute()
    print("OK: YouTube Data API v3 is enabled and working!")
    
except HttpError as e:
    if 'accessNotConfigured' in str(e) or 'has not been used' in str(e):
        print("ERROR: YouTube Data API v3 is NOT enabled!")
        print("\nPlease enable it:")
        print("1. Visit: https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=114753552651")
        print("2. Click 'Enable' button")
        print("3. Wait 1-2 minutes")
        print("4. Try again")
    else:
        print(f"ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")


