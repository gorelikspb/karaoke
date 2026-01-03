#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate HTML pages for songs from songs.json
Single source of truth - generates HTML from unified database
"""

import json
import os
from pathlib import Path

SONGS_FILE = "songs.json"
OUTPUT_DIR = Path("public/songs")
TEMPLATE_DIR = Path("public")

def generate_html(song):
    """Generate HTML page for a song"""
    
    # Build lyrics HTML
    lyrics_html = ""
    for verse in song['lyrics']['verses']:
        verse_type = verse['type']
        lines_html = "\n".join([f"                    <p>{line}</p>" for line in verse['lines']])
        lyrics_html += f'                <div class="{verse_type}">\n{lines_html}\n                </div>\n\n'
    
    # Build video clips HTML
    clips_html = ""
    if song.get('video_clips'):
        clips_list = "\n".join([
            f'                    <a href="{clip["url"]}" target="_blank" class="clip-link">\n                        {clip["title"]}\n                    </a>'
            for clip in song['video_clips']
        ])
        clips_html = f'''            <div class="video-clips">
                <h3>🎬 Клипы на эту песню</h3>
                <div class="clips-list">
{clips_list}
                </div>
            </div>'''
    else:
        clips_html = ""
    
    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Текст песни {song['title']} - {song['artist']} для караоке">
    <title>{song['title']} - {song['artist']} | Караоке</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>🎤 Караоке</h1>
            <p class="subtitle">пойте любимые песни вместе</p>
        </div>
    </header>

    <main class="container">
        <div class="song-page">
            <a href="../index.html" class="back-button">← Назад к списку</a>
            
            <div class="song-header">
                <h1>{song['title']}</h1>
                <p class="artist">{song['artist']}</p>
            </div>

            <div class="youtube-container">
                <iframe 
                    src="https://www.youtube.com/embed/{song['youtube']['video_id']}?rel=0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
                </iframe>
            </div>

            <div class="song-lyrics">
{lyrics_html}            </div>

{clips_html}
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 Караоке-сайт. Для обучения пению.</p>
            <p class="disclaimer">Музыка предоставляется через YouTube. Если видео недоступно в вашем регионе, попробуйте включить песню из другого источника.</p>
        </div>
    </footer>

    <script src="../script.js"></script>
</body>
</html>'''
    
    return html


def main():
    print("Generating HTML pages from songs.json...")
    print("=" * 50)
    
    # Load songs data
    with open(SONGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate HTML for each song
    for song in data['songs']:
        html = generate_html(song)
        output_file = OUTPUT_DIR / f"{song['filename']}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Generated: {output_file.name}")
    
    print(f"\nGenerated {len(data['songs'])} HTML pages")


if __name__ == "__main__":
    main()

