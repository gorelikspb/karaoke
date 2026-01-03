#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate YouTube Shorts metadata files from songs.json
Single source of truth - generates Shorts metadata from unified database
"""

import json
import os
from pathlib import Path

SONGS_FILE = "songs.json"
METADATA_DIR = Path("shorts_metadata")


def generate_short_metadata(song):
    """Generate metadata file for a Short"""
    
    if not song['youtube']['video_id']:
        print(f"  WARNING: No video_id for {song['id']}, skipping")
        return None
    
    short_title = f"{song['title']} - Short"
    
    description = f"Короткая версия караоке.\n\n"
    description += f"🎵 Полная версия: https://www.youtube.com/watch?v={song['youtube']['video_id']}\n\n"
    description += "Пойте вместе с любимыми песнями!\n\n"
    description += "🎤 Караоке для обучения пению\n\n"
    description += "#караоке #shorts #караокепесня"
    
    tags = ["караоке", "shorts", "караоке версия", "пойте вместе"]
    if song['artist']:
        tags.append(song['artist'].lower())
    
    content = f"TITLE: {short_title} - Караоке | {song['artist']}\n\n"
    content += "DESCRIPTION:\n"
    content += description
    content += "\n\n"
    content += "TAGS:\n"
    content += ", ".join(tags)
    content += "\n\n"
    content += "CATEGORY: Music\n"
    content += f"ARTIST: {song['artist']}\n"
    content += f"FULL_VIDEO_ID: {song['youtube']['video_id']}\n"
    content += f"FULL_VIDEO_URL: https://www.youtube.com/watch?v={song['youtube']['video_id']}\n"
    content += f"SHORT_FILENAME: {song['filename']}_short\n"
    content += "\n---\n"
    content += "Generated for YouTube Shorts upload\n"
    
    return content


def main():
    print("Generating YouTube Shorts metadata files from songs.json...")
    print("=" * 50)
    
    # Load songs data
    with open(SONGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create metadata directory
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate metadata for each song (only if video_id exists)
    count = 0
    for song in data['songs']:
        if not song['youtube']['video_id']:
            print(f"Skipping {song['id']}: no video_id")
            continue
        
        metadata_content = generate_short_metadata(song)
        if not metadata_content:
            continue
        
        output_file = METADATA_DIR / f"metadata_{song['filename']}_short.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(metadata_content)
        
        print(f"Generated: {output_file.name}")
        count += 1
    
    print(f"\nGenerated {count} Shorts metadata files")


if __name__ == "__main__":
    main()

