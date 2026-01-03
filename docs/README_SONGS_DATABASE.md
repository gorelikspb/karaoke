# Единая база данных песен (songs.json)

Система использует единый источник данных `songs.json` для всех песен. Из этого файла генерируются:

1. **HTML страницы** для сайта (`public/songs/*.html`)
2. **Метаданные для YouTube** (`video_metadata/metadata_*.txt`)
3. **Метаданные для YouTube Shorts** (`shorts_metadata/metadata_*_short.txt`)

## Структура songs.json

```json
{
  "songs": [
    {
      "id": "happy-new-year",
      "title": "Happy New Year",
      "artist": "ABBA",
      "filename": "happy-new-year",
      "youtube": {
        "video_id": "vmhgG_2MM4E",
        "shorts_id": "EGOXdMEqoIo"
      },
      "metadata": {
        "description": "...",
        "tags": ["karaoke", "abba", ...],
        "category": "Music"
      },
      "lyrics": {
        "verses": [
          {
            "type": "verse",
            "lines": ["...", "..."]
          },
          {
            "type": "chorus",
            "lines": ["...", "..."]
          }
        ]
      },
      "video_clips": [
        {
          "title": "...",
          "url": "https://..."
        }
      ]
    }
  ]
}
```

## Работа с базой данных

### Добавление новой песни

1. Отредактируйте `songs.json` и добавьте новую запись в массив `songs`
2. Запустите генераторы для создания всех файлов:

```powershell
# Генерировать HTML страницы
python scripts/generate-html-from-songs.py

# Генерировать метаданные для YouTube
python scripts/generate-youtube-metadata-from-songs.py

# Генерировать метаданные для Shorts
python scripts/generate-shorts-metadata-from-songs.py
```

### Обновление данных песни

1. Отредактируйте `songs.json`
2. Запустите соответствующий генератор

### Изменения в тексте песни

Измените `lyrics.verses` в `songs.json` и запустите:
```powershell
python generate-html-from-songs.py
```

### Изменения в метаданных YouTube

Измените `metadata` в `songs.json` и запустите:
```powershell
python generate-youtube-metadata-from-songs.py
python generate-shorts-metadata-from-songs.py
```

### Обновление YouTube ID после загрузки

После загрузки видео на YouTube обновите `youtube.video_id` в `songs.json`.
После загрузки Shorts обновите `youtube.shorts_id` в `songs.json`.

## Скрипты

### `create-songs-database.py`
Создает `songs.json` из существующих файлов (один раз, для миграции).

### `scripts/generate-html-from-songs.py`
Генерирует HTML страницы из `songs.json`.

### `scripts/generate-youtube-metadata-from-songs.py`
Генерирует метаданные для загрузки полных видео на YouTube.

### `scripts/generate-shorts-metadata-from-songs.py`
Генерирует метаданные для загрузки Shorts на YouTube.

## Преимущества

✅ **Единый источник данных** - все данные о песне в одном месте  
✅ **Прозрачность** - легко увидеть все данные песни  
✅ **Автоматизация** - генерация всех файлов из одного источника  
✅ **Консистентность** - гарантирует одинаковые данные везде  
✅ **Легко обновлять** - изменил в одном месте, сгенерировал всё заново

