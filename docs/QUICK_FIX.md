# Быстрое исправление redirect_uri_mismatch

## Простое решение

Вы создали **Web app** credentials, но для локального скрипта проще использовать **Desktop app**.

### Шаг 1: Создать Desktop app credentials

1. Откройте: https://console.cloud.google.com/apis/credentials
2. Найдите ваш OAuth 2.0 Client ID (или создайте новый)
3. Нажмите на него для редактирования
4. **ИЛИ** создайте новый:
   - "Create Credentials" → "OAuth client ID"
   - Application type: **Desktop app** (НЕ Web app!)
   - Name: любое (например, "Karaoke Desktop")
   - Create

### Шаг 2: Обновить client_secrets.json

Замените значения в файле `client_secrets.json`:

```json
{
  "installed": {
    "client_id": "ВАШ_NOVЫЙ_CLIENT_ID",
    "project_id": "karaoke-uploader",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "ВАШ_NOVЫЙ_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

### Шаг 3: Запустить снова

```bash
python upload-to-youtube.py
```

---

## Альтернатива: Использовать Web app (сложнее)

Если хотите оставить Web app credentials:

1. В Google Cloud Console → Credentials → ваш OAuth client
2. Добавьте в "Authorized redirect URIs":
   - `http://localhost:8080/`
   - `http://127.0.0.1:8080/`
3. Используйте скрипт `upload-to-youtube-web.py` (более сложный процесс авторизации)

Рекомендую первый вариант - проще и быстрее!


