"""A return is a session only while it is still inside its expiry. Two writers share one account."""

import asyncio

from adapters.memory.account_store import MemoryAccountStore
from domain.account.identity import ProviderIdentity
from tests.support import WHEN, build, handoff


def test_only_the_return_just_before_expiry_opens_a_session():
    bundle = build(handoff_ttl=30)
    outcomes = []
    for code, subject, shift in (("early", "ya-early", 29), ("exact", "ya-exact", 30), ("late", "ya-late", 31)):
        issued = handoff(bundle, code, subject, f"{code}@yandex.ru", code)
        bundle.clock.advance(shift)
        outcomes.append(bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": issued}).status_code)
    assert outcomes == [200, 401, 401]


def test_overlapping_first_sign_ins_open_one_account():
    store = MemoryAccountStore()
    identity = ProviderIdentity("ya-ada", "ada@yandex.ru", "Ада")

    async def both():
        return await asyncio.gather(store.get_or_create(identity, WHEN), store.get_or_create(identity, WHEN))

    first, second = asyncio.run(both())
    assert first.id == second.id
    assert store.count() == 1
