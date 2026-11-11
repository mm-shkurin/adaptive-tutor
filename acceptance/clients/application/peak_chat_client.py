import threading

import httpx

from clients.application.http_result import HttpResult, read_result

PEAK_CHAT_IN_FLIGHT = 15


class PeakChatClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._lock = threading.Lock()
        self._results: list[HttpResult] = []
        self._threads: list[threading.Thread] = []

    def begin_peak_load(self, token: str) -> None:
        self._results = []
        self._threads = []
        for _ in range(PEAK_CHAT_IN_FLIGHT):
            thread = threading.Thread(target=self._send_chat, args=(token,))
            self._threads.append(thread)
            thread.start()

    def join(self) -> None:
        for thread in self._threads:
            thread.join(timeout=300)

    def _send_chat(self, token: str) -> None:
        with httpx.Client(base_url=self._base_url, timeout=300) as http:
            response = http.post(
                "/api/v1/chat/messages",
                headers={"Authorization": f"Bearer {token}"},
                json={"content": "peak load baseline"},
            )
            result = read_result(response)
        with self._lock:
            self._results.append(result)
