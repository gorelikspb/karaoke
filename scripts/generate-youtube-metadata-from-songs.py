#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate YouTube metadata files from songs.json
Single source of truth - generates metadata from unified database
"""

import json
import os
from pathlib import Path

SONGS_FILE = "songs.json"
METADATA_DIR = Path("video_metadata")


def generate_metadata_file(song):
    """Generate metadata file for a song"""
    
    content = f"TITLE: {song['title']} - Караоке | {song['artist']}\n\n"
    content += "DESCRIPTION:\n"
    content += song['metadata']['description']
    content += "\n\n"
    content += "TAGS:\n"
    content += ", ".join(song['metadata']['tags'])
    content += "\n\n"
    content += f"CATEGORY: {song['metadata']['category']}\n"
    content += f"ARTIST: {song['artist']}\n"
    content += f"ORIGINAL_VIDEO_ID: {song['youtube']['video_id']}\n"
    content += f"DOWNLOAD_FILENAME: {song['filename']}\n\n"
    content += "---\n"
    content += "Generated for YouTube upload\n"
    
    return content


def main():
    print("Generating YouTube metadata files from songs.json...")
    print("=" * 50)
    
    # Load songs data
    with open(SONGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create metadata directory
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate metadata for each song
    for song in data['songs']:
        metadata_content = generate_metadata_file(song)
        output_file = METADATA_DIR / f"metadata_{song['filename']}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(metadata_content)
        
        print(f"Generated: {output_file.name}")
    
    print(f"\nGenerated {len(data['songs'])} metadata files")


if __name__ == "__main__":
    main()

