# Инструкция по настройке FreeLLMAPI в adaptive-tutor

## Шаг 1: Получите Unified API Key

1. Откройте http://localhost:3001
2. Перейдите на страницу **Keys**
3. Скопируйте ключ из заголовка страницы (выглядит как `sk-...`)

## Шаг 2: Создайте .env файл

В директории `backend/` создайте файл `.env` со следующим содержимым:

```env
# FreeLLMAPI Configuration
FREE_LLM_API_URL=http://localhost:3001/v1
FREE_LLM_API_KEY=ваш-ключ-здесь

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/adaptive_tutor

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Server
PORT=8000
HOST=0.0.0.0
```

**Важно:** Замените `ваш-ключ-здесь` на ваш unified API key.

## Шаг 3: Запустите тестовый скрипт

```bash
cd backend
venv\Scripts\activate
python test_freellmapi.py
```

## Шаг 4: Используйте в коде

```python
from infrastructure.llm.freellmapi_adapter import FreeLLMAPIClient

# Клиент автоматически использует переменные окружения
client = FreeLLMAPIClient()

response = client.chat_completion([
    {"role": "user", "content": "Привет!"}
])
print(response['content'])
```

## Структура проекта

```
backend/
├── .env                 # Ваш файл с ключами (создайте сами)
├── .env.example         # Пример конфигурации
├── requirements.txt     # Зависимости (уже установлены)
├── venv/               # Виртуальное окружение (уже создано)
├── infrastructure/
│   └── llm/
│       └── freellmapi_adapter.py  # Адаптер для FreeLLMAPI
└── test_freellmapi.py  # Тестовый скрипт
```

## Установленные зависимости

✅ FastAPI
✅ OpenAI SDK
✅ Qdrant Client
✅ PostgreSQL драйвер
✅ Pytest
✅ И другие зависимости из requirements.txt
