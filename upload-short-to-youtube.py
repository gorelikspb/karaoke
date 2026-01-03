#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to upload YouTube Shorts to YouTube
Based on upload-to-youtube.py but configured for Shorts
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

# Paths for Shorts
METADATA_DIR = "shorts_metadata"
VIDEOS_DIR = "shorts"
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
                print(f"ERROR: {CREDENTIALS_FILE} not found!")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)


def parse_metadata_file(metadata_file):
    """Parse metadata file and return dict"""
    metadata = {}
    with open(metadata_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                metadata['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('CATEGORY:'):
                metadata['category'] = line.replace('CATEGORY:', '').strip()
            elif line.startswith('ARTIST:'):
                metadata['artist'] = line.replace('ARTIST:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                current_section = 'description'
                current_content = []
            elif line.startswith('TAGS:'):
                if current_section == 'description':
                    metadata['description'] = '\n'.join(current_content).strip()
                current_section = 'tags'
                current_content = []
            elif line and not line.startswith('---'):
                if current_section:
                    current_content.append(line)
                elif line.startswith('SHORT_FILENAME:'):
                    filename_val = line.replace('SHORT_FILENAME:', '').strip()
                    metadata['filename'] = filename_val
                elif line.startswith('DOWNLOAD_FILENAME:'):
                    # Fallback for compatibility
                    metadata['filename'] = line.replace('DOWNLOAD_FILENAME:', '').strip() + '_short'
                elif line.startswith('FULL_VIDEO_ID:'):
                    metadata['full_video_id'] = line.replace('FULL_VIDEO_ID:', '').strip()
        
        if current_section == 'description':
            metadata['description'] = '\n'.join(current_content).strip()
        elif current_section == 'tags':
            tags_str = ', '.join(current_content)
            metadata['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]
    
    return metadata


def upload_video(youtube, video_path, metadata, channel_id=None):
    """Upload video to YouTube"""
    title = metadata.get('title', 'Untitled')
    description = metadata.get('description', '')
    tags = metadata.get('tags', [])
    category = metadata.get('category', '22')  # People & Blogs default
    
    # Category mapping
    category_map = {
        'Music': '10',
        'People & Blogs': '22',
        'Entertainment': '24',
        'Education': '27'
    }
    category_id = category_map.get(category, '22')
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    print(f"\nUploading video...")
    print(f"  File: {video_path}")
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    # Upload with retries
    retry = 0
    error = None
    while retry <= 3:
        try:
            if channel_id:
                request = youtube.videos().insert(
                    part=','.join(body.keys()),
                    body=body,
                    media_body=media,
                    onBehalfOfBrand=channel_id
                )
            else:
                request = youtube.videos().insert(
                    part=','.join(body.keys()),
                    body=body,
                    media_body=media
                )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"  Progress: {int(status.progress() * 100)}%", end='\r')
            
            if 'id' in response:
                print(f"\nOK: Upload successful!")
                print(f"  Video ID: {response['id']}")
                print(f"  URL: https://www.youtube.com/watch?v={response['id']}")
                return response['id']
            else:
                print("ERROR: Upload failed!")
                print(f"  Response: {response}")
                return None
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
    print("YouTube Shorts Uploader")
    print("=" * 50)
    
    # Check if metadata directory exists
    if not os.path.exists(METADATA_DIR):
        print(f"ERROR: {METADATA_DIR} directory not found!")
        sys.exit(1)
    
    if not os.path.exists(VIDEOS_DIR):
        print(f"ERROR: {VIDEOS_DIR} directory not found!")
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
    
    print(f"\nFound {len(metadata_files)} Shorts metadata files")
    
    # Ask user which Short to upload
    print("\nAvailable Shorts:")
    for i, mf in enumerate(metadata_files, 1):
        print(f"{i}. {mf.stem.replace('metadata_', '').replace('_short', '')}")
    
    try:
        selection = input("\nEnter Short number to upload (or press Enter for first): ").strip()
        if not selection:
            video_index = 0
        else:
            video_index = int(selection) - 1
            if video_index < 0 or video_index >= len(metadata_files):
                print("Invalid selection!")
                sys.exit(1)
    except (ValueError, KeyboardInterrupt, EOFError):
        video_index = 0
        print("\nUsing first Short by default")
    
    metadata_file = metadata_files[video_index]
    
    try:
        # Parse metadata
        metadata = parse_metadata_file(metadata_file)
        filename = metadata.get('filename', metadata_file.stem.replace('metadata_', ''))
        # Add _short suffix if not present
        if not filename.endswith('_short'):
            filename = f"{filename}_short"
        video_path = os.path.join(VIDEOS_DIR, f"{filename}.mp4")
        
        if not os.path.exists(video_path):
            print(f"\nERROR: Video file not found: {video_path}")
            sys.exit(1)
        
        # Upload
        video_id = upload_video(youtube, video_path, metadata, CHANNEL_ID)
        if video_id:
            print(f"\n{'='*50}")
            print("Upload successful!")
            print(f"URL: https://www.youtube.com/watch?v={video_id}")
        else:
            print("\nUpload failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Error processing {metadata_file}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
