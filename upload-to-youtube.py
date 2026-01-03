#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to automatically upload videos to YouTube using YouTube Data API v3
Uses metadata files from video_metadata/ directory
"""

import os
import json
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Paths
METADATA_DIR = "video_metadata"
VIDEOS_DIR = "downloaded_videos"
CREDENTIALS_FILE = "client_secrets.json"
TOKEN_FILE = "token.pickle"

# Channel ID for uploads (set to None to use default channel)
CHANNEL_ID = None


def authenticate():
    """Authenticate and return YouTube API service"""
    creds = None
    
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Error: {CREDENTIALS_FILE} not found!")
                print("\nPlease follow these steps:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable YouTube Data API v3")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download credentials and save as 'client_secrets.json'")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)


def parse_metadata_file(metadata_path):
    """Parse metadata file and return dict"""
    metadata = {}
    current_section = None
    content_lines = []
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('TITLE:'):
                metadata['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                current_section = 'description'
                content_lines = []
            elif line.startswith('TAGS:'):
                if current_section == 'description':
                    metadata['description'] = '\n'.join(content_lines).strip()
                current_section = 'tags'
                content_lines = []
            elif line.startswith('CATEGORY:'):
                if current_section == 'tags':
                    metadata['tags'] = ', '.join([t.strip() for t in content_lines[0].split(',')]) if content_lines else ''
                current_section = None
                metadata['category'] = line.replace('CATEGORY:', '').strip()
            elif line.startswith('DOWNLOAD_FILENAME:'):
                metadata['filename'] = line.replace('DOWNLOAD_FILENAME:', '').strip()
            elif line and current_section:
                content_lines.append(line)
    
    # Handle description if file ends without CATEGORY
    if current_section == 'description' and content_lines:
        metadata['description'] = '\n'.join(content_lines).strip()
    elif current_section == 'tags' and content_lines:
        metadata['tags'] = ', '.join([t.strip() for t in content_lines[0].split(',')])
    
    return metadata


def upload_video(youtube, video_path, metadata, channel_id=None):
    """Upload video to YouTube"""
    print(f"\nUploading: {metadata.get('title', 'Unknown')}")
    print(f"File: {video_path}")
    if channel_id:
        print(f"Channel ID: {channel_id}")
    
    # Prepare video metadata
    body = {
        'snippet': {
            'title': metadata.get('title', 'Untitled'),
            'description': metadata.get('description', ''),
            'tags': metadata.get('tags', '').split(', ') if metadata.get('tags') else [],
            'categoryId': '10'  # Music category
        },
        'status': {
            'privacyStatus': 'private',  # Set to 'private' initially, change to 'public' if needed
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Create media file upload object
    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
        mimetype='video/*'
    )
    
    # Insert video
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    # Execute upload
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print(f"OK: Upload successful! Video ID: {response['id']}")
                    print(f"  URL: https://www.youtube.com/watch?v={response['id']}")
                    return response['id']
                else:
                    print("ERROR: Upload failed!")
                    print(f"  Response: {response}")
                    return None
            else:
                print(f"  Progress: {int(status.progress() * 100)}%", end='\r')
        except Exception as e:
            error = e
            retry += 1
            if retry > 3:
                print(f"\nERROR: Upload failed after retries: {error}")
                return None
            print(f"\n  Error: {error}, retrying... ({retry}/3)")
    
    return None


def main():
    """Main function"""
    print("YouTube Video Uploader")
    print("=" * 50)
    
    # Check if metadata directory exists
    if not os.path.exists(METADATA_DIR):
        print(f"Error: {METADATA_DIR} directory not found!")
        sys.exit(1)
    
    if not os.path.exists(VIDEOS_DIR):
        print(f"Error: {VIDEOS_DIR} directory not found!")
        sys.exit(1)
    
    # Authenticate
    print("\nAuthenticating with YouTube API...")
    try:
        youtube = authenticate()
        print("OK: Authentication successful!")
    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        sys.exit(1)
    
    # Find all metadata files
    metadata_files = list(Path(METADATA_DIR).glob("metadata_*.txt"))
    if not metadata_files:
        print(f"\nNo metadata files found in {METADATA_DIR}/")
        sys.exit(1)
    
    print(f"\nFound {len(metadata_files)} metadata files")
    
    # Ask user which videos to upload
    print("\nWhich videos to upload?")
    print("1. All videos")
    print("2. Select specific videos")
    choice = input("Enter choice (1 or 2): ").strip()
    
    videos_to_upload = []
    if choice == "1":
        videos_to_upload = metadata_files
    else:
        print("\nAvailable videos:")
        for i, mf in enumerate(metadata_files, 1):
            print(f"{i}. {mf.stem.replace('metadata_', '')}")
        
        selection = input("\nEnter video numbers (comma-separated, e.g., 1,3,5): ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            videos_to_upload = [metadata_files[i] for i in indices if 0 <= i < len(metadata_files)]
        except:
            print("Invalid selection!")
            sys.exit(1)
    
    # Upload videos
    uploaded_ids = []
    for metadata_file in videos_to_upload:
        try:
            # Parse metadata
            metadata = parse_metadata_file(metadata_file)
            filename = metadata.get('filename', metadata_file.stem.replace('metadata_', ''))
            video_path = os.path.join(VIDEOS_DIR, f"{filename}.mp4")
            
            if not os.path.exists(video_path):
                print(f"\nERROR: Video file not found: {video_path}")
                continue
            
            # Upload
            video_id = upload_video(youtube, video_path, metadata, CHANNEL_ID)
            if video_id:
                uploaded_ids.append({
                    'title': metadata.get('title'),
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
        except Exception as e:
            print(f"\nERROR: Error processing {metadata_file}: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("Upload Summary:")
    print(f"Successfully uploaded: {len(uploaded_ids)}/{len(videos_to_upload)}")
    
    if uploaded_ids:
        print("\nUploaded videos:")
        for vid in uploaded_ids:
            print(f"  - {vid['title']}")
            print(f"    {vid['url']}")
        
        # Save upload info
        with open('uploaded_videos.json', 'w', encoding='utf-8') as f:
            json.dump(uploaded_ids, f, indent=2, ensure_ascii=False)
        print(f"\nUpload information saved to: uploaded_videos.json")


if __name__ == "__main__":
    main()

