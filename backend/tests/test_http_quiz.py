"""HttpQuiz posts quiz completions and normalizes messy model JSON."""

import asyncio
import json

import httpx
import pytest

from adapters.tutor.http_quiz import HttpQuiz, normalize_quiz_payload, _json_object
from domain.chat.source import Source
from domain.quiz.errors import GenerationFailed


def _quiz(handler, api_key: str = "key") -> HttpQuiz:
    return HttpQuiz(
        "http://llm.test/v1",
        api_key,
        transport=httpx.MockTransport(handler),
    )


def test_compose_returns_normalized_questions():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content.decode())
        content = json.dumps(
            {
                "questions": [
                    {
                        "text": "Q1",
                        "choices": ["a", "b", "c", "d"],
                        "correct_index": "0",
                        "page": 99,
                    }
                ]
            }
        )
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    payload = asyncio.run(
        _quiz(handler).compose("auto", "cells", 1, (Source(2, "alpha"), Source(4, "beta")))
    )
    assert payload["questions"][0]["correct_index"] == 0
    assert payload["questions"][0]["page"] == 2
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert captured["body"]["max_tokens"] == 1800
    assert "Allowed pages:" in captured["body"]["messages"][1]["content"]


def test_compose_retries_without_json_mode_when_json_mode_is_refused():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        body = json.loads(request.content.decode())
        if "response_format" in body:
            return httpx.Response(400, json={"error": "no json mode"})
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Here you go:\n"
                            + json.dumps(
                                {
                                    "questions": [
                                        {
                                            "text": "Q1",
                                            "choices": ["a", "b", "c", "d"],
                                            "correct_index": 1,
                                            "page": 2,
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            },
        )

    payload = asyncio.run(_quiz(handler).compose("auto", "cells", 1, (Source(2, "alpha"),)))
    assert calls["n"] == 2
    assert payload["questions"][0]["page"] == 2


def test_json_object_extracts_object_from_prose():
    raw = 'Sure!\n```json\n{"questions":[]}\n```\nthanks'
    assert _json_object(raw) == {"questions": []}


def test_normalize_rejects_too_few_questions():
    with pytest.raises(ValueError):
        normalize_quiz_payload({"questions": []}, 3, (Source(2, "a"),))


def test_missing_api_key_fails_without_a_network_call():
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    with pytest.raises(GenerationFailed):
        asyncio.run(_quiz(handler, api_key="").compose("auto", "cells", 3, ()))
    assert calls["n"] == 0
