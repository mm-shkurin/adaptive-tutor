import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from clients.application.chat_client import ChatClient
from statements.failed_reply_statements import REPLY_FAILED
from statements.reply_statements import MODEL, SCRIPT

PEOPLE = 20
SENDS_EACH = 5
P95_SECONDS = 3.0
P99_SECONDS = 5.0
FAILED_BUDGET_SECONDS = 5.0
QUESTION = "What does the lecture say under peak burst?"


class ChatLoadStatements:
    def given_the_chat_latency_baseline(self) -> None:
        self.burst_people: list[tuple[str, str]] = []
        for index in range(PEOPLE):
            opened = self.sessions.open_account(
                f"load{index}@example.test", f"Load{index}"
            )
            assert opened.status_code == 200
            assert opened.body is not None
            token = opened.body["access_token"]
            document_id = self._ready_pdf(f"load-{index}.pdf", token)
            seeded = self.chats.seed_search(
                token, document_id, ({"text": f"piece-{index}", "page": 1},)
            )
            assert seeded.status_code == 204
            created = self.chats.create(token, document_id)
            assert created.status_code == 201
            assert created.body is not None
            self.burst_people.append((token, created.body["id"]))
        scripted = self.chats.script_tutor(self.burst_people[0][0], SCRIPT)
        assert scripted.status_code == 204
        self.base_url = str(self.chats.http.base_url)
        self.burst_results: list[tuple[float, object]] = []
        self.failed_send = None
        self.failed_elapsed = None

    def and_each_person_has_an_askable_chat(self) -> None:
        assert len(self.burst_people) == PEOPLE

    def when_the_peak_burst_sends(self) -> None:
        jobs = [
            (token, chat_id, send_index)
            for token, chat_id in self.burst_people
            for send_index in range(SENDS_EACH)
        ]
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=PEOPLE) as pool:
            futures = [
                pool.submit(self._timed_send, token, chat_id, send_index)
                for token, chat_id, send_index in jobs
            ]
            self.burst_results = [future.result() for future in futures]
        self.burst_wall = time.perf_counter() - started
        assert self.burst_wall < 60.0

    def then_each_reply_arrives_whole(self) -> None:
        assert len(self.burst_results) == PEOPLE * SENDS_EACH
        for elapsed, sent in self.burst_results:
            assert elapsed >= 0
            assert sent.status_code == 200
            assert sent.body is not None
            assert sent.body["error"] is None
            roles = [line["role"] for line in sent.body["lines"]]
            assert "person" in roles
            assert "tutor" in roles
            tutor = next(line for line in sent.body["lines"] if line["role"] == "tutor")
            assert tutor["text"] == SCRIPT

    def then_the_replies_stay_inside_the_chat_latency_budget(self) -> None:
        samples = sorted(elapsed for elapsed, _ in self.burst_results)
        assert _percentile(samples, 95) < P95_SECONDS
        assert _percentile(samples, 99) < P99_SECONDS

    def then_a_failed_fake_is_counted_as_a_failed_reply_not_as_a_hung_send(self) -> None:
        token, chat_id = self.burst_people[0]
        armed = self.chats.fail_tutor(token)
        assert armed.status_code == 204
        client = ChatClient(self.base_url)
        start = time.perf_counter()
        sent = client.send(
            token, chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )
        elapsed = time.perf_counter() - start
        client.close()
        self.failed_send = sent
        self.failed_elapsed = elapsed
        assert elapsed < FAILED_BUDGET_SECONDS
        assert sent.status_code == 200
        assert sent.body is not None
        assert sent.body["error"] == REPLY_FAILED
        roles = [line["role"] for line in sent.body["lines"]]
        assert "person" in roles
        assert "tutor" not in roles

    def _timed_send(self, token: str, chat_id: str, send_index: int):
        client = ChatClient(self.base_url)
        try:
            start = time.perf_counter()
            sent = client.send(
                token,
                chat_id,
                f"{QUESTION} #{send_index}",
                MODEL,
                "professor",
                str(uuid4()),
            )
            elapsed = time.perf_counter() - start
            return elapsed, sent
        finally:
            client.close()


def _percentile(sorted_samples: list[float], percentile: int) -> float:
    if not sorted_samples:
        raise AssertionError("no latency samples")
    rank = max(0, min(len(sorted_samples) - 1, (percentile * len(sorted_samples) + 99) // 100 - 1))
    return sorted_samples[rank]
