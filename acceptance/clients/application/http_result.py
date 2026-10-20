from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class HttpResult:
    status_code: int
    body: dict | None


def read_result(response: httpx.Response) -> HttpResult:
    if not response.content:
        return HttpResult(response.status_code, None)
    return HttpResult(response.status_code, response.json())
