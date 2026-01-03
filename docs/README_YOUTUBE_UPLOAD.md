# Инструкция по автоматической загрузке видео на YouTube

## Предварительные требования

1. **Python библиотеки:**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **Google Cloud Project с включенным YouTube Data API v3**

## Настройка Google Cloud Project

### Шаг 1: Создание проекта

1. Перейдите на https://console.cloud.google.com/
2. Создайте новый проект или выберите существующий
3. Запишите название проекта

### Шаг 2: Включение YouTube Data API

1. В Google Cloud Console перейдите в "APIs & Services" → "Library"
2. Найдите "YouTube Data API v3"
3. Нажмите "Enable" (Включить)

### Шаг 3: Создание OAuth 2.0 Credentials

1. Перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth client ID"
3. Если запросит, настройте OAuth consent screen:
   - User Type: External
   - App name: любое (например, "Karaoke Uploader")
   - User support email: ваш email
   - Developer contact: ваш email
   - Сохраните и продолжайте
4. В "Scopes" добавьте: `https://www.googleapis.com/auth/youtube.upload`
5. Сохраните и продолжайте
6. Application type: **Desktop app**
7. Name: любое (например, "Karaoke Uploader Desktop")
8. Нажмите "Create"
9. Нажмите "Download JSON"
10. Сохраните файл как `client_secrets.json` в корневую папку проекта

### Шаг 4: Разрешения OAuth

При первом запуске скрипта откроется браузер, где нужно:
1. Войти в свой Google аккаунт
2. Разрешить приложению доступ к YouTube
3. После этого токен сохранится в `token.pickle` для последующих запусков

## Использование

### Запуск скрипта

```bash
python upload-to-youtube.py
```

### Процесс загрузки

1. Скрипт проверит наличие `client_secrets.json`
2. При первом запуске откроется браузер для авторизации
3. После авторизации выберите:
   - Загрузить все видео
   - Выбрать конкретные видео
4. Скрипт загрузит выбранные видео с метаданными
5. Информация о загруженных видео сохранится в `uploaded_videos.json`

### Важные замечания

- **Приватность видео:** По умолчанию видео загружаются как **private**. Вы можете изменить это в коде, изменив `'privacyStatus': 'private'` на `'public'` или `'unlisted'`
- **Категория:** Все видео загружаются в категорию "Music" (ID: 10)
- **Токен:** После первой авторизации токен сохраняется в `token.pickle`. Если возникнут проблемы, удалите этот файл и авторизуйтесь заново

## Структура файлов

```
karaoke/
├── upload-to-youtube.py       # Основной скрипт
├── client_secrets.json        # OAuth credentials (нужно скачать)
├── token.pickle              # Сохраненный токен (создается автоматически)
├── uploaded_videos.json      # Список загруженных видео (создается после загрузки)
├── video_metadata/           # Метаданные для загрузки
└── downloaded_videos/        # Видеофайлы
```

## Troubleshooting

### Ошибка: "client_secrets.json not found"
- Убедитесь, что файл скачан из Google Cloud Console
- Проверьте, что файл находится в корневой папке проекта
- Проверьте название файла (должно быть точно `client_secrets.json`)

### Ошибка: "This app isn't verified"
- Это нормально для тестового приложения
- Нажмите "Advanced" → "Go to [Your App Name] (unsafe)"
- Разрешите доступ

### Ошибка: "The request cannot be completed because you have exceeded your quota"
- У вас превышен лимит запросов YouTube API
- Лимит: 6,000 units в день (1 загрузка = ~1,600 units)
- Максимум ~3-4 видео в день бесплатно
- Можно запросить увеличение квоты в Google Cloud Console

### Видео загружается долго
- Это нормально, зависит от размера файла и скорости интернета
- Скрипт показывает прогресс в процентах
- Не закрывайте окно терминала во время загрузки


