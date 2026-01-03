#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple script to create YouTube Short from one video
YouTube Shorts: 59 seconds, 1:1 aspect ratio (1080x1080 square)

Usage:
    python create-short-simple.py [video_number]
    
    video_number: Optional. Number from the list (1-N). 
                  If not provided, will prompt interactively.
                  If non-interactive and not provided, uses first video.
    
Examples:
    python create-short-simple.py 1    # Create short from first video
    python create-short-simple.py      # Interactive selection
"""

import os
import subprocess
import sys
from pathlib import Path

VIDEOS_DIR = "downloaded_videos"
SHORTS_DIR = "shorts"
SHORTS_MAX_DURATION = 59  # seconds (YouTube Shorts max is 60, using 59 to be safe)
SHORTS_WIDTH = 1080
SHORTS_HEIGHT = 1080  # Square format (1:1) for Shorts

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      text=True,
                      check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def get_video_duration(video_path):
    """Get video duration in seconds"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"ERROR: Could not get video duration: {e}")
        return None

def create_short(input_video, output_video, duration=59):
    """Create YouTube Short from video"""
    
    duration = min(duration, SHORTS_MAX_DURATION)
    
    print(f"\nCreating Short:")
    print(f"  Input: {input_video}")
    print(f"  Output: {output_video}")
    print(f"  Duration: {duration}s")
    print(f"  Resolution: {SHORTS_WIDTH}x{SHORTS_HEIGHT} (1:1 square)")
    
    # FFmpeg command
    # Strategy: 
    # 1. Scale to fit width (1080px), maintaining aspect ratio
    # 2. Add 10% padding (black bars) top and bottom
    # 3. Crop to square (1080x1080) from center
    # This ensures text is not cut off
    
    # Calculate padding: 10% of height = height * 0.1
    # So new height = height * 1.2, then crop to 1080x1080
    padding_percent = 0.1
    padded_height = int(SHORTS_HEIGHT * (1 + padding_percent * 2))  # 10% top + 10% bottom
    
    # First scale to fit width, then pad vertically, then crop to square
    # scale=1080:-1:force_original_aspect_ratio=decrease - scale to width 1080, maintain aspect
    # pad=1080:1320:(ow-iw)/2:(oh-ih)/2:black - pad to 1080x1320 (1080 + 10%*2 = 1320) with black
    # crop=1080:1080:0:120 - crop to 1080x1080, starting from y=120 (10% of 1320 = 132)
    
    crop_y_offset = int(padded_height * padding_percent)  # 10% from top
    
    cmd = [
        'ffmpeg',
        '-i', str(input_video),
        '-t', str(duration),
        '-vf', f'scale={SHORTS_WIDTH}:-1:force_original_aspect_ratio=decrease,pad={SHORTS_WIDTH}:{padded_height}:(ow-iw)/2:(oh-ih)/2:black,crop={SHORTS_WIDTH}:{SHORTS_HEIGHT}:0:{crop_y_offset}',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        str(output_video)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"ERROR: {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("YouTube Shorts Creator")
    print("=" * 50)
    
    # Check ffmpeg
    if not check_ffmpeg():
        print("ERROR: ffmpeg not found!")
        print("\nPlease install ffmpeg first.")
        print("See: INSTALL_FFMPEG.md")
        print("\nQuick install: winget install ffmpeg")
        sys.exit(1)
    
    print("OK: ffmpeg found")
    
    # Create shorts directory
    os.makedirs(SHORTS_DIR, exist_ok=True)
    
    # List videos
    videos = list(Path(VIDEOS_DIR).glob("*.mp4"))
    if not videos:
        print(f"ERROR: No videos in {VIDEOS_DIR}/")
        sys.exit(1)
    
    print(f"\nAvailable videos:")
    for i, v in enumerate(videos, 1):
        dur = get_video_duration(v)
        print(f"{i}. {v.stem} ({dur:.1f}s)" if dur else f"{i}. {v.stem}")
    
    # Select video - from command line argument or interactive
    if len(sys.argv) > 1:
        try:
            num = int(sys.argv[1])
            if num < 1 or num > len(videos):
                print(f"ERROR: Invalid video number. Must be 1-{len(videos)}")
                sys.exit(1)
            video = videos[num - 1]
            print(f"\nSelected video {num}: {video.stem}")
        except ValueError:
            print(f"ERROR: Invalid video number: {sys.argv[1]}")
            sys.exit(1)
    else:
        # Interactive selection
        try:
            num = int(input(f"\nSelect video (1-{len(videos)}): "))
            if num < 1 or num > len(videos):
                print("Invalid!")
                sys.exit(1)
            video = videos[num - 1]
        except (ValueError, KeyboardInterrupt, EOFError):
            # If no input available (non-interactive), use first video
            print("\nNo input provided, using first video by default")
            video = videos[0]
    
    # Get duration
    duration = get_video_duration(video)
    if not duration:
        sys.exit(1)
    
    # Use first 59 seconds or full video if shorter
    clip_duration = min(duration, SHORTS_MAX_DURATION)
    
    # Output file
    output = Path(SHORTS_DIR) / f"{video.stem}_short.mp4"
    
    # Create short
    print(f"\nCreating short from first {clip_duration:.1f} seconds...")
    if create_short(video, output, clip_duration):
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"\nOK: Short created!")
        print(f"  File: {output}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"\nReady to upload to YouTube Shorts!")
    else:
        print("\nERROR: Failed to create short")
        sys.exit(1)

if __name__ == "__main__":
    main()

