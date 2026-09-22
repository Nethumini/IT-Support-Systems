"""The explanation that follows an action.

An action leaves the user holding a measurement and nothing else - "C: 16.14 GB
free (95.7% used)" - so they have to ask what it means. These cover the endpoint
that answers unasked.

The model is mocked throughout. The point is not what it writes, but that the
prompt carries the real measured state, that a failure names its cause, and that
it costs exactly one request - the free tier allows about twenty a day, and an
explanation that quietly cost three would end a demo early.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.remediation import RemediationRequestDB, fingerprint


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def completed_request(db):
    """A disk check that ran on a device and was verified."""
    request = RemediationRequestDB(
        user_email="admin@acme.com",
        reported_problem="my disk is full",
        action_id="check_disk_space",
        parameters={},
        device_id="dev_win1",
        action_fingerprint=fingerprint("check_disk_space", {}, "dev_win1"),
        status="completed",
        verification_status="verified_success",
        evidence=[],
        execution_result={
            "success": True,
            "driver": "agent",
            "output": '[{"Name":"C","Free":17332764672}]',
            "state_before": {"disk_mount": "C:", "disk_free_gb": 16.14, "disk_used_percent": 95.7},
            "state_after": {"disk_mount": "C:", "disk_free_gb": 16.14, "disk_used_percent": 95.7},
        },
        post_check={"reason": "Diagnostic action completed without changing system state."},
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


class FakeModel:
    """Records the prompt and returns whatever it was told to."""

    def __init__(self, text="Your C: drive is almost full.", raises=False):
        self.text = text
        self.raises = raises
        self.calls = []

    def generate_content(self, prompt):
        self.calls.append(prompt)
        if self.raises:
            raise RuntimeError("quota exhausted")
        return type("R", (), {"text": self.text})()


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeModel()

    def _agent():
        return type("A", (), {"model": model})()

    monkeypatch.setattr(
        "app.services.agents.llm_conversation_agent.get_llm_conversation_agent",
        _agent,
    )
    return model


async def call_explain(db, request, user_email="admin@acme.com", role="system_admin"):
    from app.api.endpoints.remediation import explain_remediation

    user = type("U", (), {"email": user_email, "role": role})()
    return await explain_remediation(request.id, db=db, current_user=user)


@pytest.mark.asyncio
async def test_the_explanation_comes_back(db, completed_request, fake_model):
    result = await call_explain(db, completed_request)
    assert result["explanation"] == "Your C: drive is almost full."


@pytest.mark.asyncio
async def test_it_costs_exactly_one_request(db, completed_request, fake_model):
    """A chat turn in agent mode costs three: classify, reply, choose an action.

    Two of those are wasted here - the action has already run and its result is
    in hand - so this path calls the model directly. On a twenty-a-day tier the
    difference decides whether a demo finishes.
    """
    await call_explain(db, completed_request)
    assert len(fake_model.calls) == 1


@pytest.mark.asyncio
async def test_the_prompt_carries_the_measured_state(db, completed_request, fake_model):
    """The explanation must be about what was measured, not invented."""
    await call_explain(db, completed_request)
    prompt = fake_model.calls[0]

    assert "16.14" in prompt
    assert "95.7" in prompt
    assert "check_disk_space" in prompt
    assert "my disk is full" in prompt
    assert "verified_success" in prompt


@pytest.mark.asyncio
async def test_it_is_told_not_to_claim_a_fix(db, completed_request, fake_model):
    """A diagnostic changed nothing, and the wording must not imply otherwise."""
    await call_explain(db, completed_request)
    assert "Never claim the problem is fixed" in fake_model.calls[0]


@pytest.mark.asyncio
async def test_a_quota_failure_says_so(db, completed_request, monkeypatch):
    """The caller must be able to tell why there is no explanation.

    Returning a bare null made an exhausted quota look identical to the feature
    not being built - which is how the first failure was reported.
    """
    failing = FakeModel(raises=True)  # raises "quota exhausted"
    monkeypatch.setattr(
        "app.services.agents.llm_conversation_agent.get_llm_conversation_agent",
        lambda: type("A", (), {"model": failing})(),
    )

    result = await call_explain(db, completed_request)

    assert result["explanation"] is None
    assert result["reason"] == "quota"
    assert "quota exhausted" in result["detail"]


@pytest.mark.asyncio
async def test_other_failures_are_reported_separately(db, completed_request, monkeypatch):
    """A configuration fault needs fixing; a spent quota needs waiting."""
    class Broken:
        def generate_content(self, prompt):
            raise ValueError("API key not configured")

    monkeypatch.setattr(
        "app.services.agents.llm_conversation_agent.get_llm_conversation_agent",
        lambda: type("A", (), {"model": Broken()})(),
    )

    result = await call_explain(db, completed_request)

    assert result["reason"] == "unavailable"
    assert "API key" in result["detail"]


@pytest.mark.asyncio
async def test_an_empty_answer_is_not_posted_as_a_message(db, completed_request, monkeypatch):
    monkeypatch.setattr(
        "app.services.agents.llm_conversation_agent.get_llm_conversation_agent",
        lambda: type("A", (), {"model": FakeModel(text="   ")})(),
    )

    result = await call_explain(db, completed_request)
    assert result["explanation"] is None


@pytest.mark.asyncio
async def test_someone_elses_remediation_is_refused(db, completed_request, fake_model):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await call_explain(db, completed_request, user_email="other@acme.com", role="end_user")

    assert exc.value.status_code == 403
