#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get channel ID for a YouTube channel by handle or name
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
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
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)

def get_channel_by_handle(youtube, handle):
    """Get channel by handle (e.g., @karaoke-e2t)"""
    # Remove @ if present
    handle = handle.lstrip('@')
    
    try:
        request = youtube.channels().list(
            part='id,snippet',
            forHandle=handle
        )
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]
            return {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'handle': channel['snippet'].get('customUrl', 'N/A')
            }
    except Exception as e:
        print(f"Error searching by handle: {e}")
    
    return None

def list_user_channels(youtube):
    """List all channels accessible by the authenticated user"""
    try:
        request = youtube.channels().list(
            part='id,snippet',
            mine=True
        )
        response = request.execute()
        
        if response.get('items'):
            print("\nYour accessible channels:")
            print("=" * 50)
            for i, channel in enumerate(response['items'], 1):
                print(f"{i}. {channel['snippet']['title']}")
                print(f"   Channel ID: {channel['id']}")
                print(f"   Handle: @{channel['snippet'].get('customUrl', 'N/A')}")
                print()
            return response['items']
    except Exception as e:
        print(f"Error listing channels: {e}")
    
    return []

print("Finding YouTube channel...")
print("=" * 50)

youtube = authenticate()

# Try to find by handle
print("\nSearching for channel @karaoke-e2t...")
channel = get_channel_by_handle(youtube, "@karaoke-e2t")

if channel:
    print(f"\nFound channel:")
    print(f"  Name: {channel['title']}")
    print(f"  Channel ID: {channel['id']}")
    print(f"  Handle: @{channel['handle']}")
    print(f"\nUse this Channel ID in upload script: {channel['id']}")
else:
    print("\nChannel not found by handle. Listing all your channels...")
    channels = list_user_channels(youtube)
    
    if channels:
        print("\nPlease select the correct channel ID from the list above.")
    else:
        print("\nNo channels found. Make sure you have access to the channel.")


