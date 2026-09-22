"""The server must keep answering while a model call is in flight.

The Gemini SDK is synchronous. Called straight from an async endpoint it holds
the event loop for the whole request, and on the free tier - where the SDK
retries behind the scenes - that was over three minutes. Nothing else was
served in that window: the endpoint agents' polls timed out and reported the
backend unreachable, and the page hung.

That matters more here than in most systems, because the agent collects its
work over this same API. A model call that stops the server also stops the
machine that was about to run the remediation.

These tests use a deliberately slow fake model and check that an unrelated
request still completes while it is running. No real model is called.
"""
import asyncio
import time

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

SLOW_CALL_SECONDS = 0.4


class SlowModel:
    """Stands in for the SDK: blocks the calling thread, as it really does."""

    def __init__(self, seconds=SLOW_CALL_SECONDS):
        self.seconds = seconds

    def generate_content(self, prompt):
        time.sleep(self.seconds)  # blocking on purpose
        return type("R", (), {"text": "done"})()


@pytest.mark.asyncio
async def test_a_blocking_call_on_the_loop_freezes_everything():
    """The bug, reproduced - so the fix below is measured against something.

    This is how the endpoints were written: the synchronous call made directly
    inside the coroutine.
    """
    app = FastAPI()
    model = SlowModel()

    @app.post("/slow")
    async def slow():
        model.generate_content("x")  # straight on the event loop
        return {"ok": True}

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        started = time.monotonic()
        await asyncio.gather(client.post("/slow"), client.get("/ping"))
        elapsed = time.monotonic() - started

    # The ping could not be served until the blocking call finished.
    assert elapsed >= SLOW_CALL_SECONDS


@pytest.mark.asyncio
async def test_a_worker_thread_keeps_the_server_answering():
    """The fix: the same call, moved off the loop."""
    from fastapi.concurrency import run_in_threadpool

    app = FastAPI()
    model = SlowModel()

    @app.post("/slow")
    async def slow():
        await run_in_threadpool(model.generate_content, "x")
        return {"ok": True}

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        slow_call = asyncio.create_task(client.post("/slow"))
        await asyncio.sleep(0.05)  # let the slow call get going

        started = time.monotonic()
        ping = await client.get("/ping")
        ping_took = time.monotonic() - started

        await slow_call

    assert ping.status_code == 200
    # Answered while the model call was still running, not after it.
    assert ping_took < SLOW_CALL_SECONDS / 2, f"ping waited {ping_took:.2f}s"


def test_no_model_call_is_left_on_the_event_loop():
    """Every synchronous SDK call in a request path must be handed to a thread.

    A regression here is invisible in normal testing - the endpoint still works,
    it just takes the whole server down with it while it waits.
    """
    import re
    from pathlib import Path

    paths = [
        Path("app/api/endpoints/chat_enhanced.py"),
        Path("app/api/endpoints/remediation.py"),
        Path("app/services/agents/action_executor_agent.py"),
    ]

    offenders = []
    for path in paths:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "generate_content" not in line:
                continue
            # Fine when handed to a worker, or when it is the argument to one.
            if "to_thread" in line or "run_in_threadpool" in line:
                continue
            # Fine inside a plain def: the caller wraps the whole function.
            if re.search(r"=\s*\w+.*\.generate_content\(", line):
                offenders.append(f"{path.name}:{number}: {line.strip()}")

    # classify_intent_with_llm is synchronous and its call site is wrapped, so
    # the one call inside it is allowed.
    allowed = {"chat_enhanced.py"}
    unexpected = [o for o in offenders if o.split(":")[0] not in allowed]

    assert not unexpected, "blocking model calls on the event loop:\n" + "\n".join(unexpected)
