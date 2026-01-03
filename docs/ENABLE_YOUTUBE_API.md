# Включение YouTube Data API v3

## Ошибка
```
YouTube Data API v3 has not been used in project 114753552651 before or it is disabled
```

## Решение

### Шаг 1: Включить API

1. Перейдите по прямой ссылке:
   **https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=114753552651**

2. Или вручную:
   - Откройте: https://console.cloud.google.com/
   - Выберите проект (ID: 114753552651)
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "YouTube Data API v3"
   - Нажмите "Enable" (Включить)

### Шаг 2: Подождать

После включения API подождите 1-2 минуты, чтобы изменения применились.

### Шаг 3: Попробовать снова

```bash
python upload-to-youtube.py
```

## Проверка

После включения API вы должны увидеть в консоли:
- "APIs & Services" → "Enabled APIs"
- В списке должен быть "YouTube Data API v3"


