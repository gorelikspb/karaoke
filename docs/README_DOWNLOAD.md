# Инструкция по скачиванию видео

## Быстрый старт

1. **Установите yt-dlp** (если еще не установлен):
   ```powershell
   pip install yt-dlp
   ```
   Или скачайте с: https://github.com/yt-dlp/yt-dlp/releases

2. **Запустите скрипт**:
   ```powershell
   .\download-videos-simple.ps1
   ```
   
   Или подробный скрипт:
   ```powershell
   .\download-videos.ps1
   ```

3. **Видео будут сохранены** в папку `downloaded_videos/`

## Список скачиваемых видео

- RcWJkY8Qsm4 - Песня о звёздах
- c2Y1UGWceU0 - С новым годом, крошка  
- Wq9tPd5OXMQ - Светлая полоса
- Ukn0xjnsLko - No Surprises
- kaBRnhxPLdE - Last Christmas
- J3fBefc1_js - Happy New Year
- 6E0BRIN3Z0c - Happy Xmas
- FZxI62c34RA - Звезда по имени Солнце
- I1SBneovIV8 - Небо Лондона

## Дополнительные опции

Если нужно скачать только аудио:
```powershell
yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=VIDEO_ID"
```

Если нужно выбрать качество:
```powershell
yt-dlp -f "best[height<=720]" "https://www.youtube.com/watch?v=VIDEO_ID"
```



