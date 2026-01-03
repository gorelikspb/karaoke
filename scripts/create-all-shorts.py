#!/usr/bin/env python3
"""
Create YouTube Shorts for all videos
"""
import subprocess
import sys
from pathlib import Path

VIDEOS_DIR = "downloaded_videos"
SHORTS_DIR = "shorts"

def create_short(video_path):
    """Create a short for a video"""
    video_name = video_path.stem
    output_path = Path(SHORTS_DIR) / f"{video_name}_short.mp4"
    
    # Skip if already exists
    if output_path.exists():
        print(f"Skip: {video_name}_short.mp4 (already exists)")
        return True
    
    print(f"\nCreating Short: {video_name}")
    
    # Call create-short-simple.py with video number
    # We need to find the video number first
    videos = sorted(list(Path(VIDEOS_DIR).glob("*.mp4")))
    try:
        video_num = videos.index(video_path) + 1
        result = subprocess.run(
            [sys.executable, "create-short-simple.py", str(video_num)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"OK: {video_name}_short.mp4 created")
            return True
        else:
            print(f"ERROR: Failed to create {video_name}_short.mp4")
            print(result.stderr)
            return False
    except ValueError:
        print(f"ERROR: Video not found in list")
        return False

def main():
    print("Creating Shorts for all videos")
    print("=" * 50)
    
    # Create shorts directory
    Path(SHORTS_DIR).mkdir(exist_ok=True)
    
    # Get all videos
    videos = sorted(list(Path(VIDEOS_DIR).glob("*.mp4")))
    if not videos:
        print(f"ERROR: No videos in {VIDEOS_DIR}/")
        sys.exit(1)
    
    print(f"\nFound {len(videos)} videos")
    
    # Create shorts for all videos
    success_count = 0
    for video in videos:
        if create_short(video):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"Created {success_count}/{len(videos)} Shorts")
    print(f"Shorts saved in: {SHORTS_DIR}/")

if __name__ == "__main__":
    main()

