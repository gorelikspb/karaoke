#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update all YouTube videos to public and set "not for kids"
Обновляет все видео на канале: делает публичными и устанавливает "not for kids"
"""

import json
import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Paths
UPLOADED_VIDEOS_FILE = "uploaded_videos.json"
CREDENTIALS_FILE = "client_secrets.json"
TOKEN_FILE = "token.pickle"


def authenticate():
    """Authenticate and return YouTube API service"""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"ERROR: {CREDENTIALS_FILE} not found!")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)


def update_video_status(youtube, video_id, title):
    """Update video to public and set not for kids"""
    title_safe = title[:50].encode('ascii', 'ignore').decode('ascii')
    print(f"\nUpdating: {title_safe}")
    print(f"  Video ID: {video_id}")
    
    try:
        # First, get current video details
        video_response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            print(f"  ERROR: Video not found")
            return False
        
        video = video_response['items'][0]
        snippet = video['snippet']
        status = video['status']
        
        # Update status
        status['privacyStatus'] = 'public'
        status['selfDeclaredMadeForKids'] = False
        
        # Update video
        update_response = youtube.videos().update(
            part='status',
            body={
                'id': video_id,
                'status': status
            }
        ).execute()
        
        print(f"  OK: Updated to public, not for kids")
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("Update YouTube Videos to Public")
    print("=" * 60)
    
    # Load uploaded videos
    if not Path(UPLOADED_VIDEOS_FILE).exists():
        print(f"ERROR: {UPLOADED_VIDEOS_FILE} not found!")
        sys.exit(1)
    
    with open(UPLOADED_VIDEOS_FILE, 'r', encoding='utf-8') as f:
        uploaded_videos = json.load(f)
    
    print(f"\nFound {len(uploaded_videos)} videos to update")
    
    # Authenticate
    print("\nAuthenticating with YouTube API...")
    try:
        youtube = authenticate()
        print("OK: Authentication successful!")
    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        sys.exit(1)
    
    # Update each video
    updated = 0
    failed = 0
    
    for video in uploaded_videos:
        video_id = video['video_id']
        title = video['title']
        
        if update_video_status(youtube, video_id, title):
            updated += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"Successfully updated: {updated}/{len(uploaded_videos)}")
    if failed > 0:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()

