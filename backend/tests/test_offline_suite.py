"""The suite's offline guarantee, tested.

``conftest.py`` installs a placeholder key and refuses every model call. A
guard nobody has seen trip proves nothing, so these tests make it trip.
"""
import google.generativeai as genai
import pytest

from app.config import Settings, get_settings


def test_the_suite_runs_on_the_placeholder_key_not_a_real_one(offline_guard):
    settings = get_settings()
    assert settings.google_api_key == offline_guard.placeholder_key
    assert settings.openai_api_key == offline_guard.placeholder_key


def test_production_settings_still_default_to_no_key():
    """The placeholder lives in the test process only."""
    assert Settings.model_fields["google_api_key"].default == ""
    assert Settings.model_fields["openai_api_key"].default == ""


def test_a_model_call_is_refused_and_recorded(offline_guard):
    calls = offline_guard.attempted_calls
    already = len(calls)

    with pytest.raises(RuntimeError, match="Offline test suite"):
        genai.GenerativeModel("gemini-2.5-flash").generate_content("hello")
    with pytest.raises(RuntimeError, match="Offline test suite"):
        genai.embed_content(model="models/gemini-embedding-001", content="hello")

    assert calls[already:] == [
        "GenerativeModel.generate_content",
        "genai.embed_content",
    ]
    # Made on purpose here; any other test doing the same fails.
    del calls[already:]
