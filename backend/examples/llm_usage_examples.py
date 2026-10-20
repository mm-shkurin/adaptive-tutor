"""
Примеры использования LLM в adaptive-tutor
Покрывает все основные сценарии: чат, викторины, объяснения, RAG
"""

import sys
import os
import io

# Устанавливаем UTF-8 для вывода в Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Добавляем parent directory в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from infrastructure.llm.freellmapi_adapter import FreeLLMAPIClient
from domain.llm.llm_service import LLMService, ChatMessage


def example_1_basic_chat():
    """Пример 1: Базовый чат с выбором модели"""
    print("=" * 60)
    print("[EXAMPLE 1] Basic Chat with Model Selection")
    print("=" * 60)

    client = FreeLLMAPIClient()
    service = LLMService(client)

    # Чат с авто-выбором модели
    response = service.chat([
        ChatMessage(role="system", content="Ты полезный ассистент."),
        ChatMessage(role="user", content="Привет! Представься.")
    ], model="auto")

    print(f"Response: {response}\n")


def example_2_chat_with_specific_model():
    """Пример 2: Чат с конкретной моделью"""
    print("=" * 60)
    print("[EXAMPLE 2] Chat with Specific Model")
    print("=" * 60)

    client = FreeLLMAPIClient()
    service = LLMService(client)

    # Чат с конкретной моделью (более компактный промпт)
    response = service.chat([
        ChatMessage(role="system", content="Ты преподаватель."),
        ChatMessage(role="user", content="Объясни Big O notation в 2-3 предложениях.")
    ], model="qwen/qwen3.8-27b", temperature=0.5, max_tokens=300)

    print(f"Response: {response}\n")


def example_3_generate_quiz():
    """Пример 3: Генерация викторины"""
    print("=" * 60)
    print("[EXAMPLE 3] Quiz Generation")
    print("=" * 60)

    client = FreeLLMAPIClient()
    service = LLMService(client)

    # Генерация викторины по теме (меньше вопросов)
    quiz = service.generate_quiz(
        topic="Python lists",
        difficulty="medium",
        num_questions=2
    )

    print(f"Generated Quiz: {quiz}\n")


def example_4_generate_explanation():
    """Пример 4: Генерация объяснения"""
    print("=" * 60)
    print("[EXAMPLE 4] Explanation Generation")
    print("=" * 60)

    client = FreeLLMAPIClient()
    service = LLMService(client)

    # Генерация объяснения (более компактное)
    explanation = service.generate_explanation(
        topic="Recursion",
        difficulty="easy",
        examples=True
    )

    print(f"Topic: {explanation.topic}")
    print(f"Explanation: {explanation.explanation}\n")


def example_5_rag_chat():
    """Пример 5: RAG-чат с контекстом"""
    print("=" * 60)
    print("[EXAMPLE 5] RAG Chat with Context")
    print("=" * 60)

    client = FreeLLMAPIClient()
    service = LLMService(client)

    # Имитация извлеченного контента из документов
    retrieved_context = [
        "Стек (stack) - это структура данных LIFO (Last In, First Out).",
        "Очередь (queue) - это структура данных FIFO (First In, First Out).",
        "Стек используется для рекурсии, undo/redo операций.",
        "Очередь используется для планирования задач, буферизации."
    ]

    # RAG-чат
    response = service.rag_chat(
        query="В чем разница между стеком и очередью?",
        retrieved_context=retrieved_context
    )

    print(f"Response: {response}\n")


def example_6_conversation_history():
    """Пример 6: Чат с историей диалога"""
    print("=" * 60)
    print("[EXAMPLE 6] Chat with Conversation History")
    print("=" * 60)

    client = FreeLLMAPIClient()
    service = LLMService(client)

    # История диалога
    history = [
        ChatMessage(role="user", content="Что такое RAG?"),
        ChatMessage(role="assistant", content="RAG - это Retrieval Augmented Generation, метод который использует внешние данные для улучшения ответов LLM."),
        ChatMessage(role="user", content="Какие преимущества у RAG?")
    ]

    response = service.chat(history, model="auto")

    print(f"Response: {response}\n")


def example_7_get_available_models():
    """Пример 7: Получение списка моделей"""
    print("=" * 60)
    print("[EXAMPLE 7] Get Available Models")
    print("=" * 60)

    client = FreeLLMAPIClient()
    models = client.get_available_models()

    print(f"Total models: {len(models)}")
    print("\nPopular models:")
    popular = ["auto", "fusion", "qwen/qwen3.8-27b", "gemma-4-31b"]
    for model in models:
        if any(p in model for p in popular):
            print(f"  - {model}")
    print()


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("LLM Usage Examples for adaptive-tutor")
    print("*" * 60)
    print("\n")

    # Запуск всех примеров
    example_1_basic_chat()
    example_2_chat_with_specific_model()
    example_3_generate_quiz()
    example_4_generate_explanation()
    example_5_rag_chat()
    example_6_conversation_history()
    example_7_get_available_models()

    print("*" * 60)
    print("All examples completed!")
    print("*" * 60)
