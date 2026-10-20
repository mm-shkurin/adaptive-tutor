"""
FreeLLMAPI Adapter для adaptive-tutor
Инфраструктурный слой для LLM запросов через FreeLLMAPI
"""

from openai import OpenAI
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()


class FreeLLMAPIClient:
    """Клиент для работы с FreeLLMAPI"""

    def __init__(
        self,
        base_url: str = "http://localhost:3001/v1",
        api_key: Optional[str] = None
    ):
        """
        Инициализация клиента FreeLLMAPI

        Args:
            base_url: URL FreeLLMAPI endpoint
            api_key: Unified API key (или из env FREE_LLM_API_KEY)
        """
        self.base_url = base_url
        self.api_key = api_key or os.getenv("FREE_LLM_API_KEY")

        if not self.api_key:
            raise ValueError(
                "FREE_LLM_API_KEY не найден. "
                "Установите переменную окружения или передайте в конструктор."
            )

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "auto",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict:
        """
        Отправить запрос к LLM

        Args:
            messages: Список сообщений [{"role": "user", "content": "..."}]
            model: Имя модели
            max_tokens: Максимальное количество токенов
            temperature: Температура (креативность)
            stream: Стриминг ответа

        Returns:
            Dict с ответом от модели
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream
            )

            if stream:
                return response  # Для стриминга
            else:
                return {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
        except Exception as e:
            raise RuntimeError(f"Ошибка при запросе к FreeLLMAPI: {e}")

    def get_available_models(self) -> List[str]:
        """Получить список доступных моделей"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении списка моделей: {e}")


# Пример использования
if __name__ == "__main__":
    # Создание клиента
    client = FreeLLMAPIClient(
        base_url="http://localhost:3001/v1",
        api_key="YOUR_UNIFIED_KEY_HERE"  # Или через env FREE_LLM_API_KEY
    )

    # Пример запроса
    messages = [
        {"role": "system", "content": "Ты опытный преподаватель."},
        {"role": "user", "content": "Объясни что такое hexagonal architecture."}
    ]

    response = client.chat_completion(messages)
    print(f"Ответ: {response['content']}")
    print(f"Токены: {response['usage']['total_tokens']}")
