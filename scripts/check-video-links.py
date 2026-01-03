#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check video links on website"""

import json
from pathlib import Path

SONGS_FILE = "songs.json"
UPLOADED_FILE = "uploaded_videos.json"

print("=" * 80)
print("Video Links on Website")
print("=" * 80)

# Load songs
with open(SONGS_FILE, 'r', encoding='utf-8') as f:
    songs_data = json.load(f)

# Load uploaded videos
with open(UPLOADED_FILE, 'r', encoding='utf-8') as f:
    uploaded_videos = json.load(f)

# Create map
uploaded_map = {v['video_id']: v for v in uploaded_videos}

print("\nSongs on website:")
print("-" * 80)

results = []
for song in songs_data['songs']:
    video_id = song['youtube']['video_id']
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    
    in_uploaded = video_id in uploaded_map
    status = "OK" if in_uploaded else "NOT FOUND"
    
    result = {
        'title': song['title'],
        'artist': song['artist'],
        'video_id': video_id,
        'embed_url': embed_url,
        'watch_url': watch_url,
        'status': status
    }
    results.append(result)

# Write to file
with open('video-links-check.txt', 'w', encoding='utf-8') as f:
    f.write("Video Links on Website\n")
    f.write("=" * 80 + "\n\n")
    
    for r in results:
        f.write(f"{r['title']} - {r['artist']}\n")
        f.write(f"  Video ID: {r['video_id']}\n")
        f.write(f"  Embed URL: {r['embed_url']}\n")
        f.write(f"  Watch URL: {r['watch_url']}\n")
        f.write(f"  Status: {r['status']}\n")
        if r['status'] == "OK":
            f.write(f"  Title in uploaded: {uploaded_map[r['video_id']]['title']}\n")
        f.write("\n")
    
    f.write("=" * 80 + "\n")
    f.write(f"Total songs: {len(results)}\n")
    f.write(f"In uploaded_videos.json: {sum(1 for r in results if r['status'] == 'OK')}\n")

print(f"\nResults saved to: video-links-check.txt")
print(f"Total songs: {len(results)}")
print(f"In uploaded_videos.json: {sum(1 for r in results if r['status'] == 'OK')}")
