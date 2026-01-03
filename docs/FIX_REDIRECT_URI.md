# Исправление ошибки redirect_uri_mismatch

## Проблема
У вас созданы **Web app** credentials, а для локального скрипта нужны **Desktop app** credentials.

## Решение (выберите один вариант)

### Вариант 1: Добавить redirect URI для Web app (быстро)

1. Перейдите в Google Cloud Console: https://console.cloud.google.com/
2. APIs & Services → Credentials
3. Найдите ваши OAuth 2.0 Client ID credentials
4. Нажмите на них для редактирования
5. В разделе "Authorized redirect URIs" добавьте:
   ```
   http://localhost:8080/
   http://localhost:8080
   http://127.0.0.1:8080/
   http://127.0.0.1:8080
   ```
6. Сохраните изменения
7. Попробуйте снова запустить скрипт

### Вариант 2: Создать Desktop app credentials (рекомендуется)

1. Перейдите в Google Cloud Console: https://console.cloud.google.com/
2. APIs & Services → Credentials
3. Нажмите "Create Credentials" → "OAuth client ID"
4. Application type: выберите **"Desktop app"** (не Web app!)
5. Name: любое имя (например, "Karaoke Uploader Desktop")
6. Нажмите "Create"
7. Скопируйте Client ID и Client secret
8. Обновите файл `client_secrets.json` с новыми значениями

## После исправления

Запустите снова:
```bash
python test-upload.py
```

Или сразу для загрузки:
```bash
python upload-to-youtube.py
```


