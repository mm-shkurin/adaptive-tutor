"""HttpTutor posts OpenAI chat completions and maps failures to ReplyFailed."""

import asyncio
import json

import httpx
import pytest

from adapters.tutor.http_tutor import HttpTutor
from domain.chat.source import Source
from usecase.chat.errors import ReplyFailed


def _tutor(handler, api_key: str = "key") -> HttpTutor:
    return HttpTutor(
        "http://llm.test/v1",
        api_key,
        transport=httpx.MockTransport(handler),
    )


def test_a_readable_completion_returns_the_assistant_text():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "From the lecture."}}]},
        )

    text = asyncio.run(
        _tutor(handler).answer(
            "auto",
            "professor",
            "What is X?",
            (Source(2, "X is two."),),
        )
    )
    assert text == "From the lecture."
    assert captured["url"] == "http://llm.test/v1/chat/completions"
    assert captured["body"]["model"] == "auto"
    assert "Material:" in captured["body"]["messages"][1]["content"]
    assert "page 2" in captured["body"]["messages"][1]["content"]
    assert "What is X?" in captured["body"]["messages"][1]["content"]


def test_a_missing_api_key_fails_without_a_network_call():
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json={"choices": [{"message": {"content": "no"}}]})

    with pytest.raises(ReplyFailed):
        asyncio.run(_tutor(handler, api_key="").answer("auto", "professor", "Q?", ()))
    assert calls["n"] == 0


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(400, json={"error": "bad"}),
        httpx.Response(500, text="down"),
        httpx.Response(200, json={"choices": [{"message": {"content": ""}}]}),
        httpx.Response(200, json={"choices": []}),
        httpx.Response(200, text="not-json"),
    ],
)
def test_a_bad_completion_is_reply_failed(response):
    def handler(_request: httpx.Request) -> httpx.Response:
        return response

    with pytest.raises(ReplyFailed):
        asyncio.run(_tutor(handler).answer("auto", "professor", "Q?", ()))


def test_a_timeout_is_reply_failed():
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    with pytest.raises(ReplyFailed):
        asyncio.run(_tutor(handler).answer("auto", "professor", "Q?", ()))


def test_five_year_old_uses_the_plain_words_system_prompt():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        messages = json.loads(request.content.decode())["messages"]
        captured["system"] = messages[0]["content"]
        captured["user"] = messages[1]["content"]
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    asyncio.run(_tutor(handler).answer("auto", "five_year_old", "Q?", ()))
    assert "five-year-old" in captured["system"]
    assert "same language" in captured["system"]
    assert "same language" in captured["user"]


def test_an_unknown_listed_model_falls_back_to_auto():
    models = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        models.append(body["model"])
        if body["model"] != "auto":
            return httpx.Response(404, json={"error": "missing"})
        return httpx.Response(200, json={"choices": [{"message": {"content": "fallback"}}]})

    text = asyncio.run(_tutor(handler).answer("qwen/qwen3-32b", "professor", "Q?", ()))
    assert text == "fallback"
    assert models == ["qwen/qwen3-32b", "auto"]
