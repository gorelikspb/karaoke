#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete workflow: Download video from YouTube, upload to your channel, add to database
Просто дайте ссылку - скрипт скачает, загрузит на ваш канал и добавит в базу

Usage:
    python add-song-from-youtube-complete.py "https://www.youtube.com/watch?v=VIDEO_ID"
"""

import json
import sys
import subprocess
import re
import os
from pathlib import Path

SONGS_FILE = "songs.json"
VIDEOS_DIR = "downloaded_videos"
METADATA_DIR = "video_metadata"

# Import upload functions
sys.path.insert(0, str(Path(__file__).parent))
try:
    from upload_to_youtube import authenticate, parse_metadata_file, upload_video
except ImportError:
    # Fallback: import from file
    import importlib.util
    upload_script = Path('upload-to-youtube.py')
    spec = importlib.util.spec_from_file_location("upload_module", upload_script)
    upload_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upload_module)
    authenticate = upload_module.authenticate
    parse_metadata_file = upload_module.parse_metadata_file
    upload_video = upload_module.upload_video


def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtu\.be/([^?]+)',
        r'youtube\.com/embed/([^?]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def download_video(video_id, output_filename):
    """Download video using yt-dlp"""
    print(f"Downloading video {video_id}...")
    
    output_path = Path(VIDEOS_DIR) / f"{output_filename}.mp4"
    
    Path(VIDEOS_DIR).mkdir(exist_ok=True)
    
    cmd = [
        'python', '-m', 'yt_dlp',
        '-f', 'best[ext=mp4]/best',
        '-o', str(output_path),
        '--no-warnings',
        f'https://www.youtube.com/watch?v={video_id}'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"OK: Video downloaded to {output_path}")
        return output_path
    else:
        print(f"ERROR: Download failed: {result.stderr}")
        return None


def get_video_info(video_id):
    """Get video info using yt-dlp"""
    try:
        cmd = [
            'python', '-m', 'yt_dlp',
            '--dump-json',
            '--no-warnings',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None


def create_metadata_file(filename, song_title, artist, video_id_original):
    """Create metadata file for upload"""
    metadata_content = f"""TITLE: {song_title} - Караоке | {artist}

DESCRIPTION:
Караоке версия песни '{song_title}' {artist}.

Пойте вместе с любимыми песнями!

🎤 Караоке для обучения пению

#караоке #{artist.lower().replace(' ', '')} #{filename.replace('-', '')} #караокепесня

TAGS:
караоке, {artist.lower()}, {song_title.lower()}, караоке версия, пойте вместе

CATEGORY: Music
ARTIST: {artist}
ORIGINAL_VIDEO_ID: {video_id_original}
DOWNLOAD_FILENAME: {filename}

---
Generated for YouTube upload
"""
    
    Path(METADATA_DIR).mkdir(exist_ok=True)
    metadata_file = Path(METADATA_DIR) / f"metadata_{filename}.txt"
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write(metadata_content)
    
    return metadata_file


def extract_artist_from_title(title):
    """Try to extract artist from title"""
    clean_title = re.sub(r'\s*\(?karaoke\s+version\)?\s*$', '', title, flags=re.IGNORECASE)
    clean_title = re.sub(r'\s*\(?караоке\s+версия\)?\s*$', '', clean_title, flags=re.IGNORECASE)
    
    patterns = [
        r'(.+?)\s*-\s*(.+)$',
        r'(.+?)\s*\|\s*(.+)$',
        r'(.+?)\s*by\s+(.+)$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_title, re.IGNORECASE)
        if match:
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            
            part1_words = len(part1.split())
            part2_words = len(part2.split())
            
            if part1_words <= 3 and part2_words >= 1:
                artist = part1
                song = part2
            else:
                artist = part2
                song = part1
            
            return song.strip(), artist.strip()
    
    return clean_title, ""


def create_filename(title, artist):
    """Create filename from title and artist"""
    filename = title.lower()
    
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    
    result = ""
    for char in filename:
        if char in translit_map:
            result += translit_map[char]
        elif char.isalnum() or char in ['-', '_']:
            result += char
        elif char in [' ', '.', ',', '!', '?']:
            result += '-'
    
    result = re.sub(r'-+', '-', result)
    result = result.strip('-')
    
    return result


def add_song_to_database(song_data):
    """Add song to songs.json"""
    with open(SONGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_ids = [s['id'] for s in data['songs']]
    if song_data['id'] in existing_ids:
        print(f"\nSong with ID '{song_data['id']}' already exists!")
        try:
            overwrite = input("Overwrite? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        if overwrite != 'y':
            return False
        data['songs'] = [s for s in data['songs'] if s['id'] != song_data['id']]
    
    data['songs'].append(song_data)
    
    with open(SONGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return True


def main():
    print("=" * 60)
    print("Complete workflow: Download -> Upload -> Add to database")
    print("=" * 60)
    
    # Get YouTube URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("\nYouTube video URL to download: ").strip()
    
    # Extract video ID
    original_video_id = extract_video_id(url)
    if not original_video_id:
        print("ERROR: Could not extract video ID from URL")
        sys.exit(1)
    
    print(f"\nOriginal Video ID: {original_video_id}")
    print("Getting video info...")
    
    # Get video info
    video_info = get_video_info(original_video_id)
    if not video_info:
        print("ERROR: Could not get video info")
        sys.exit(1)
    
    title = video_info.get('title', '')
    print(f"Title: {title[:80]}...")
    
    # Extract song title and artist
    song_title, artist = extract_artist_from_title(title)
    print(f"Extracted: '{song_title}' by '{artist}'")
    
    # Confirm
    try:
        song_title = input(f"Song title [{song_title}]: ").strip() or song_title
        artist = input(f"Artist [{artist}]: ").strip() or artist
    except (EOFError, KeyboardInterrupt):
        print("\nUsing extracted values")
    
    if not artist:
        print("ERROR: Artist is required!")
        sys.exit(1)
    
    # Create filename
    filename = create_filename(song_title, artist)
    try:
        filename = input(f"Filename/ID [{filename}]: ").strip() or filename
    except (EOFError, KeyboardInterrupt):
        pass
    
    # Download video
    print("\n" + "=" * 60)
    video_path = download_video(original_video_id, filename)
    if not video_path:
        print("ERROR: Could not download video")
        sys.exit(1)
    
    # Create metadata
    print("\nCreating metadata file...")
    metadata_file = create_metadata_file(filename, song_title, artist, original_video_id)
    print(f"OK: Metadata created: {metadata_file}")
    
    # Upload to YouTube
    print("\n" + "=" * 60)
    print("Uploading video to your YouTube channel...")
    
    try:
        metadata = parse_metadata_file(metadata_file)
        youtube = authenticate()
        uploaded_video_id = upload_video(youtube, str(video_path), metadata, None)
    except Exception as e:
        print(f"\nERROR: Upload failed: {e}")
        print("\nYou can upload manually later using:")
        print(f"  python upload-to-youtube.py")
        sys.exit(1)
    
    if not uploaded_video_id:
        print("\nERROR: Upload failed!")
        print("You can upload manually later using:")
        print(f"  python upload-to-youtube.py")
        sys.exit(1)
    
    print(f"\nOK: Video uploaded! New video_id: {uploaded_video_id}")
    
    # Add to database
    print("\n" + "=" * 60)
    song_data = {
        'id': filename,
        'title': song_title,
        'artist': artist,
        'filename': filename,
        'youtube': {
            'video_id': uploaded_video_id,  # Use uploaded video ID!
            'shorts_id': None
        },
        'metadata': {
            'description': f"Караоке версия песни '{song_title}' {artist}.\n\nПойте вместе с любимыми песнями!\n\n🎤 Караоке для обучения пению\n\n#караоке #{artist.lower().replace(' ', '')} #{filename.replace('-', '')} #караокепесня",
            'tags': ['караоке', artist.lower(), song_title.lower(), 'караоке версия', 'пойте вместе'],
            'category': 'Music'
        },
        'lyrics': {
            'verses': []
        },
        'video_clips': []
    }
    
    print("Adding song to database...")
    if add_song_to_database(song_data):
        print("OK: Song added to songs.json")
    else:
        print("ERROR: Could not add song")
        sys.exit(1)
    
    # Generate HTML
    print("\nGenerating HTML page...")
    result = subprocess.run([sys.executable, 'scripts/generate-html-from-songs.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("OK: HTML page generated")
    
    print("\n" + "=" * 60)
    print("Done!")
    print(f"Song '{song_title}' added with video ID: {uploaded_video_id}")
    print(f"HTML page: public/songs/{filename}.html")


if __name__ == "__main__":
    main()
