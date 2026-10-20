"""
Domain Layer - LLM Service
Бизнес-логика для работы с LLM в adaptive-tutor
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Сообщение чата"""
    role: str  # system, user, assistant
    content: str


@dataclass
class QuizQuestion:
    """Вопрос викторины"""
    question: str
    options: List[str]
    correct_answer: int
    explanation: str


@dataclass
class GeneratedExplanation:
    """Сгенерированное объяснение"""
    topic: str
    explanation: str
    examples: List[str]
    difficulty: str


class LLMService:
    """
    Сервис для работы с LLM на domain уровне
    Определяет бизнес-логику без привязки к конкретной реализации
    """

    def __init__(self, llm_client):
        """
        Args:
            llm_client: Инфраструктурный адаптер (FreeLLMAPIClient)
        """
        self.llm_client = llm_client

    def chat(
        self,
        messages: List[ChatMessage],
        model: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Базовый чат с AI

        Args:
            messages: Список сообщений
            model: Модель LLM (auto для авто-выбора)
            temperature: Температура (креативность)
            max_tokens: Максимальное количество токенов

        Returns:
            Ответ от LLM
        """
        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = self.llm_client.chat_completion(
            messages=message_dicts,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response['content']

    def generate_quiz(
        self,
        topic: str,
        difficulty: str = "medium",
        num_questions: int = 5,
        context: Optional[str] = None
    ) -> List[QuizQuestion]:
        """
        Генерация викторины по теме

        Args:
            topic: Тема викторины
            difficulty: Сложность (easy, medium, hard)
            num_questions: Количество вопросов
            context: Дополнительный контент (из RAG)

        Returns:
            Список вопросов викторины
        """
        system_prompt = f"""Generate {num_questions} quiz questions about {topic} ({difficulty} level).
Format: JSON array with question, options (4), correct_answer (0-3), explanation."""

        user_prompt = f"Quiz about: {topic}"
        if context:
            user_prompt += f"\nContext: {context[:500]}"  # Ограничиваем контекст

        response = self.chat([
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ], temperature=0.5, max_tokens=1000)

        # TODO: Парсинг JSON ответа
        # Для простоты возвращаем сырой ответ
        return [{"raw_response": response}]

    def generate_explanation(
        self,
        topic: str,
        difficulty: str = "medium",
        examples: bool = True,
        context: Optional[str] = None
    ) -> GeneratedExplanation:
        """
        Генерация объяснения по теме

        Args:
            topic: Тема для объяснения
            difficulty: Сложность (easy, medium, hard)
            examples: Добавлять примеры
            context: Дополнительный контент (из RAG)

        Returns:
            Сгенерированное объяснение
        """
        system_prompt = f"Explain {topic} at {difficulty} level. {'Include examples.' if examples else ''}"

        user_prompt = f"Explain: {topic}"
        if context:
            user_prompt += f"\nContext: {context[:500]}"  # Ограничиваем контекст

        response = self.chat([
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ], temperature=0.6, max_tokens=800)

        return GeneratedExplanation(
            topic=topic,
            explanation=response,
            examples=[],  # TODO: извлечь примеры из ответа
            difficulty=difficulty
        )

    def rag_chat(
        self,
        query: str,
        retrieved_context: List[str],
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """
        RAG-чат с использованием контекста из документов

        Args:
            query: Запрос пользователя
            retrieved_context: Извлеченный контент из документов
            conversation_history: История диалога

        Returns:
            Ответ с учетом контекста
        """
        # Ограничиваем контекст
        context_str = "\n\n".join(retrieved_context[:3])  # Берем только первые 3

        system_prompt = "Answer using only the provided context. Cite sources."

        user_prompt = f"Context: {context_str}\n\nQuestion: {query}"

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ]

        if conversation_history:
            # Ограничиваем историю
            messages = [ChatMessage(role="system", content=system_prompt)] + conversation_history[-2:] + [
                ChatMessage(role="user", content=user_prompt)
            ]

        return self.chat(messages, temperature=0.3, max_tokens=500)
