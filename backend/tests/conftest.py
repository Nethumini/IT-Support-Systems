"""Test-suite configuration: offline, and provably so.

The suite must run from a clean clone - no ``backend/.env``, no provider key,
no network - and it must never spend the free-tier model quota or send test
text to a provider. Two things make that hold.

**A placeholder key, set before anything imports the application.** Several
services refuse to construct without a Gemini key even when the test never
reaches a model call. The settings object is cached for the life of the
process, so the values below must be in the environment before the first
test module imports ``app``; conftest runs first. Environment variables take
precedence over ``backend/.env``, so a real key on a developer's machine can
never reach a test either. The placeholder exists only here - production
settings still default to no key.

**A guard on the only two ways the code can reach the provider.** Every model
call in the application goes through ``GenerativeModel.generate_content`` or
``genai.embed_content``. Both are replaced for the whole run by a function
that refuses and records the attempt, and any test that makes one fails -
even when the code under test catches the error and falls back, which would
otherwise hide it. A test that stubs the model itself replaces the guard for
its own duration, which is not an external call.
"""
import os

#: Unmistakably not a credential. Never used outside the test process.
OFFLINE_PLACEHOLDER_KEY = "offline-test-placeholder-not-a-real-key"

os.environ["GOOGLE_API_KEY"] = OFFLINE_PLACEHOLDER_KEY
os.environ["OPENAI_API_KEY"] = OFFLINE_PLACEHOLDER_KEY
# Settings parses DEBUG as a boolean. A shell that exports DEBUG=release, as
# the development machine's did, stopped the whole suite at import.
os.environ["DEBUG"] = "false"

import google.generativeai as genai  # noqa: E402
import pytest  # noqa: E402

_attempted_calls = []


def _refuse(entry_point):
    def refuse(*_args, **_kwargs):
        _attempted_calls.append(entry_point)
        raise RuntimeError(
            f"Offline test suite: {entry_point} would contact the model provider."
        )
    return refuse


genai.GenerativeModel.generate_content = _refuse("GenerativeModel.generate_content")
genai.embed_content = _refuse("genai.embed_content")


@pytest.fixture
def offline_guard():
    """The placeholder key and the record of refused calls, for testing the
    guard itself."""
    from types import SimpleNamespace

    return SimpleNamespace(
        placeholder_key=OFFLINE_PLACEHOLDER_KEY,
        attempted_calls=_attempted_calls,
    )


@pytest.fixture(autouse=True)
def _no_live_model_calls():
    """Fail any test that tried to reach the provider, caught or not."""
    already = len(_attempted_calls)
    yield
    attempted = _attempted_calls[already:]
    if attempted:
        pytest.fail(
            "Tried to reach the model provider: " + ", ".join(attempted),
            pytrace=False,
        )
