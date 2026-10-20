# FreeLLMAPI Integration Guide for adaptive-tutor

## 📋 Что реализовано

### Domain Layer (`domain/llm/llm_service.py`)
Бизнес-логика для работы с LLM без привязки к конкретной реализации:
- ✅ **Basic Chat** - базовый чат с выбором модели
- ✅ **Quiz Generation** - генерация викторин по теме
- ✅ **Explanation Generation** - генерация объяснений
- ✅ **RAG Chat** - чат с использованием контекста из документов

### Infrastructure Layer (`infrastructure/llm/freellmapi_adapter.py`)
Адаптер для FreeLLMAPI:
- ✅ Работа с OpenAI-совместимым API
- ✅ Автоматический выбор модели (`auto`)
- ✅ Обработка ошибок
- ✅ Получение списка моделей

### Examples (`examples/llm_usage_examples.py`)
7 примеров использования:
1. Базовый чат с авто-выбором модели
2. Чат с конкретной моделью
3. Генерация викторины
4. Генерация объяснения
5. RAG-чат с контекстом
6. Чат с историей диалога
7. Получение списка моделей

---

## 🚀 Как использовать в проекте

### 1. Чат с AI-агентом (выбор моделей)

```python
from domain.llm.llm_service import LLMService, ChatMessage
from infrastructure.llm.freellmapi_adapter import FreeLLMAPIClient

client = FreeLLMAPIClient()
service = LLMService(client)

# Авто-выбор модели (рекомендуется)
response = service.chat([
    ChatMessage(role="system", content="Ты преподаватель."),
    ChatMessage(role="user", content="Объясни что-то.")
], model="auto")

# Или конкретная модель
response = service.chat([
    ChatMessage(role="user", content="Привет!")
], model="qwen/qwen3.8-27b")
```

### 2. Генерация викторин/тестов

```python
# Генерация викторины по теме
quiz = service.generate_quiz(
    topic="Python lists and dictionaries",
    difficulty="medium",
    num_questions=5
)

# С контекстом из RAG
quiz = service.generate_quiz(
    topic="Machine Learning basics",
    difficulty="hard",
    num_questions=10,
    context=retrieved_documents
)
```

### 3. Генерация объяснений

```python
# Простое объяснение
explanation = service.generate_explanation(
    topic="Recursion in programming",
    difficulty="easy",
    examples=True
)

# С контекстом из документов
explanation = service.generate_explanation(
    topic="Neural Networks",
    difficulty="medium",
    examples=True,
    context=retrieved_text
)
```

### 4. RAG-система (поиск по документам)

```python
# Извлечение контекста из Qdrant
retrieved_context = qdrant_client.search(query, top_k=5)

# RAG-чат
response = service.rag_chat(
    query="Что такое Big O notation?",
    retrieved_context=retrieved_context,
    conversation_history=history
)
```

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                    │
│  /chat, /quiz, /explanation, /rag-chat endpoints         │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│              Application Layer (Use Cases)                │
│  ChatUseCase, QuizUseCase, ExplanationUseCase            │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│                Domain Layer (Business Logic)               │
│  LLMService, ChatMessage, QuizQuestion, Explanation      │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│            Infrastructure Layer (Adapters)                 │
│  FreeLLMAPIClient, QdrantAdapter, PostgreSQLAdapter      │
└───────────────────────────────────────────────────────────┘
```

---

## 📝 Примеры FastAPI endpoints

### Chat Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from domain.llm.llm_service import LLMService, ChatMessage
from infrastructure.llm.freellmapi_adapter import FreeLLMAPIClient

app = FastAPI()
llm_client = FreeLLMAPIClient()
llm_service = LLMService(llm_client)

class ChatRequest(BaseModel):
    message: str
    model: str = "auto"
    temperature: float = 0.7

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        response = llm_service.chat([
            ChatMessage(role="user", content=request.message)
        ], model=request.model, temperature=request.temperature)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Quiz Generation Endpoint

```python
class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    num_questions: int = 5

@app.post("/api/quiz/generate")
async def generate_quiz(request: QuizRequest):
    try:
        quiz = llm_service.generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        return {"quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### RAG Chat Endpoint

```python
class RAGChatRequest(BaseModel):
    query: str
    conversation_history: List[dict] = []

@app.post("/api/rag/chat")
async def rag_chat(request: RAGChatRequest):
    try:
        # Извлечение контекста из Qdrant
        retrieved_context = qdrant_client.search(request.query, top_k=5)

        # Конвертация истории
        history = [
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in request.conversation_history
        ]

        # RAG-чат
        response = llm_service.rag_chat(
            query=request.query,
            retrieved_context=retrieved_context,
            conversation_history=history
        )
        return {"response": response, "sources": retrieved_context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎯 Доступные модели

Популярные модели из FreeLLMAPI:
- `auto` - автоматический выбор (рекомендуется)
- `fusion` - fusion-модель
- `qwen/qwen3.8-27b` - Qwen 3.8 27B
- `gemma-4-31b` - Gemma 4 31B
- `claude-opus-4-5` - Claude Opus 4.5
- `claude-sonnet-4-5` - Claude Sonnet 4.5

Полный список: `python -c "from infrastructure.llm.freellmapi_adapter import FreeLLMAPIClient; print(FreeLLMAPIClient().get_available_models())"`

---

## 🧪 Тестирование

Запустить все примеры:
```bash
cd backend
python examples/llm_usage_examples.py
```

Запустить базовый тест:
```bash
cd backend
python test_freellmapi.py
```

---

## 📚 Следующие шаги

1. **Интеграция с Qdrant** - реализовать retrieval для RAG
2. **Парсинг JSON** - улучшить парсинг ответов для викторин
3. **Rate limiting** - добавить лимиты на запросы
4. **Caching** - кэширование ответов для повторных запросов
5. **Streaming** - добавить стриминг для длинных ответов
6. **User profiles** - персонализация моделей для разных пользователей

---

## 🔗 Полезные ссылки

- FreeLLMAPI: http://localhost:3001
- FreeLLMAPI Models: https://freellmapi.co/models.html
- OpenAI SDK Docs: https://github.com/openai/openai-python
