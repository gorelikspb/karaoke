# Установка FFmpeg для Windows

FFmpeg нужен для создания YouTube Shorts из видео.

## Вариант 1: Через winget (рекомендуется)

```powershell
winget install ffmpeg
```

## Вариант 2: Через Chocolatey

Если у вас установлен Chocolatey:
```powershell
choco install ffmpeg
```

## Вариант 3: Ручная установка

1. Скачайте FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. Выберите: `ffmpeg-release-essentials.zip`
3. Распакуйте в `C:\ffmpeg\`
4. Добавьте в PATH:
   - Откройте "Система" → "Дополнительные параметры системы"
   - "Переменные среды"
   - В "Системные переменные" найдите "Path"
   - Добавьте: `C:\ffmpeg\bin`
5. Перезапустите терминал

## Проверка

После установки проверьте:
```powershell
ffmpeg -version
```

Если видите версию - всё готово!


