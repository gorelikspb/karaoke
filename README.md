# Караоке проект

Веб-сайт с караоке-версиями песен и инструменты для управления видео на YouTube.

## Структура проекта

### Основные папки

- **`public/`** - Веб-сайт (публикуется на GitHub)
  - `index.html` - Главная страница
  - `songs/` - Страницы отдельных песен (9 песен)
  - `styles.css` - Стили сайта
  - `script.js`, `lyrics-sync.js` - JavaScript для сайта

- **`scripts/`** - Скрипты для автоматизации
  - Генерация HTML и метаданных
  - Скачивание и загрузка видео
  - Создание Shorts
  - Утилиты

- **`docs/`** - Документация
  - Инструкции по настройке YouTube API
  - Руководства по использованию
  - Описание базы данных

- **`downloaded_videos/`** - Скачанные полные видео (MP4, не коммитятся)
- **`shorts/`** - YouTube Shorts (MP4, не коммитятся)
- **`video_metadata/`** - Метаданные для полных видео (генерируются автоматически)
- **`shorts_metadata/`** - Метаданные для Shorts (генерируются автоматически)

### Основные файлы

#### Конфигурация и данные

- **`songs.json`** - ⭐ **Единая база данных всех песен** (источник истины)
  - Содержит всю информацию о каждой песне: название, исполнитель, текст, YouTube ID, метаданные
  - Из этого файла генерируются HTML страницы, метаданные YouTube и Shorts
- **`uploaded_videos.json`** - Информация о загруженных на YouTube видео (не коммитится)
- **`client_secrets.json`** - Креденшелы Google API (не коммитится)
- **`token.pickle`** - Токен аутентификации YouTube API (не коммитится)
- **`requirements-upload.txt`** - Python зависимости для YouTube API

#### Основные скрипты (в корне)

- **`add-song-from-youtube-complete.py`** - ⭐ Добавить новую песню из YouTube ссылки
  - Автоматически скачивает, загружает на ваш канал, добавляет в базу данных
- **`upload-to-youtube.py`** - Загрузить видео на YouTube через API
- **`upload-short-to-youtube.py`** - Загрузить YouTube Short через API

#### Скрипты в `scripts/`

**Генерация (из songs.json):**
- `generate-html-from-songs.py` - Генерировать HTML страницы
- `generate-youtube-metadata-from-songs.py` - Генерировать метаданные YouTube
- `generate-shorts-metadata-from-songs.py` - Генерировать метаданные Shorts

**Скачивание:**
- `download-videos-simple.ps1` - Скачать видео с YouTube (использует yt-dlp)

**Создание Shorts:**
- `create-short-simple.py` - Создать YouTube Short из видео (59 сек, квадрат 1080x1080)
- `create-all-shorts.py` - Создать Shorts для всех видео

**Загрузка:**
- `upload-all-shorts.py` - Загрузить все Shorts на YouTube
- `upload-shorts-except-abba.py` - Загрузить Shorts (кроме уже загруженных)

**Утилиты:**
- `check-video-links.py` - Проверить соответствие ссылок на сайте и в базе данных
- `update-videos-to-public.py` - Обновить статус видео на YouTube (публичные, not for kids)
- `get-channel-id.py` - Получить ID YouTube канала
- `check-api-status.py` - Проверить статус YouTube API
- `install-ffmpeg.ps1` - Установить ffmpeg

### Документация

См. папку `docs/` для подробных инструкций:
- `README_ADD_SONG.md` - Как добавить новую песню
- `README_SONGS_DATABASE.md` - Описание базы данных songs.json
- `README_YOUTUBE_UPLOAD.md` - Настройка и использование YouTube API
- `README_UPLOAD.md` - Общая информация о загрузке видео
- `README_DOWNLOAD.md` - Информация о скачивании видео
- И другие руководства по настройке

## Работа с песнями

### ⭐ Быстрое добавление новой песни

**Важно:** Все видео должны быть загружены на ваш YouTube канал!

**Просто вставьте ссылку на YouTube караоке-видео:**
```powershell
python add-song-from-youtube-complete.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Скрипт автоматически:
1. Скачает видео с YouTube
2. Загрузит на ваш YouTube канал
3. Добавит в базу данных с video_id с вашего канала
4. Создаст HTML страницу
5. Сгенерирует метаданные для YouTube и Shorts

Подробнее: см. `docs/README_ADD_SONG.md`

### Единый источник данных - songs.json

Все данные о песнях хранятся в `songs.json`. Из этого файла генерируются:
- HTML страницы для сайта
- Метаданные для YouTube (полные видео)
- Метаданные для YouTube Shorts

**Ручное редактирование (если нужно):**
1. Отредактируйте `songs.json`
2. Запустите генераторы:
   ```powershell
   python scripts/generate-html-from-songs.py
   python scripts/generate-youtube-metadata-from-songs.py
   python scripts/generate-shorts-metadata-from-songs.py
   ```

Подробнее: см. `docs/README_SONGS_DATABASE.md`

## Что публикуется на GitHub

**Публикуется (публичные файлы):**
- `public/` - весь веб-сайт
- `songs.json` - база данных песен
- `scripts/` - все скрипты
- `docs/` - документация
- `README.md` - этот файл
- `requirements-upload.txt` - зависимости Python

**НЕ публикуется (приватные файлы):**
- `downloaded_videos/` - видео файлы
- `shorts/` - Shorts видео файлы
- `video_metadata/`, `shorts_metadata/` - генерируемые метаданные
- `client_secrets.json` - API ключи
- `token.pickle` - токены авторизации
- `uploaded_videos.json` - приватная информация о загрузках
- `*.code-workspace` - настройки IDE

## Технологии

- **Веб-сайт**: HTML, CSS, JavaScript
- **Скачивание видео**: yt-dlp (Python)
- **Обработка видео**: ffmpeg
- **YouTube API**: google-api-python-client
- **Скрипты**: Python, PowerShell

## Статус проекта

- ✅ 9 полных видео скачано и загружено на YouTube
- ✅ 9 YouTube Shorts создано
- ✅ Веб-сайт с 9 песнями
- ✅ Все видео опубликованы публично
- ⏳ Shorts еще не загружены на YouTube (есть метаданные, готовы к загрузке)
