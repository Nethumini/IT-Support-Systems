"""Integration tests for the remediation workflow through the HTTP API.

novelty.md 13.12 asks for integration tests as well as unit tests. The tests in
``test_remediation_service.py`` drive the service object directly; these go
through the running application - routing, authentication, request validation
and the JSON that a browser actually receives.

That boundary is where several of the guarantees live. A rule enforced in the
service but not reachable through the API is a rule the system does not have,
and a rule enforced only in the frontend is not a rule at all.

Everything runs against an in-memory database and the simulated driver, so the
suite needs no server, no Windows machine and no API key.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.endpoints.remediation as remediation_api
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.services.execution import SimulatedDriver, SimulatedSystem

PASSWORD = "test-password-123"

#: Whoever reports the problem, whoever approves, and someone unconnected.
USERS = [
    ("bethany.williams@acme-soft.com", "staff"),
    ("ravi.patel@acme-soft.com", "support_l2"),
    ("olu.adeyemi@acme-soft.com", "staff"),
]


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one in-memory database shared by every session
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def driver():
    return SimulatedDriver(SimulatedSystem())


@pytest.fixture
def client(session_factory, driver, monkeypatch):
    """The application, talking to a scratch database and a simulated machine."""
    from app.models.user import UserDB

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(remediation_api.service, "_driver", driver)

    db = session_factory()
    for email, role in USERS:
        db.add(UserDB(
            email=email,
            name=email.split("@")[0].replace(".", " ").title(),
            hashed_password=get_password_hash(PASSWORD),
            role=role,
            is_active=True,
        ))
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def auth(client, email=USERS[0][0]):
    response = client.post("/api/v1/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def propose(client, headers, action_id="clear_temp_files", parameters=None, **overrides):
    """A proposal with strong evidence on the user's own machine."""
    payload = {
        "reported_problem": "My C drive is full and I cannot save files",
        "action_id": action_id,
        "parameters": parameters or {},
        "diagnosis": "Temporary files have filled the disk",
        "evidence": [{"kb_id": "KB-007", "similarity_score": 0.82}],
        "catalogue_risk": "low",
        "factors": {
            "impact": 1,
            "confidence_rating": 3,
            "evidence_quality": 3,
            "irreversibility": 1,
            "affected_scope": 1,
        },
    }
    payload.update(overrides)
    return client.post("/api/v1/remediation/propose", json=payload, headers=headers)


def medium_risk(client, headers, action_id, parameters):
    """A proposal that must take the human-approval route."""
    return propose(
        client, headers,
        action_id=action_id,
        parameters=parameters,
        catalogue_risk="medium",
        factors={
            "impact": 2,
            "confidence_rating": 3,
            "evidence_quality": 3,
            "irreversibility": 1,
            "affected_scope": 1,
        },
    )


def approve(client, headers, remediation_id):
    response = client.post(
        "/api/v1/remediation/approve",
        json={"remediation_id": remediation_id},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()["approval_token"]


def execute(client, headers, remediation_id, token=None):
    body = {"remediation_id": remediation_id}
    if token is not None:
        body["token"] = token
    return client.post("/api/v1/remediation/execute", json=body, headers=headers)


# --------------------------------------------------------------------------
# Authentication
#
# novelty.md 13.6 and 13.10: these endpoints decide what runs on a machine, so
# an unauthenticated caller must not reach any of them.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("method,path,body", [
    ("get", "/api/v1/remediation/actions", None),
    ("post", "/api/v1/remediation/propose", {}),
    ("post", "/api/v1/remediation/approve", {"remediation_id": 1}),
    ("post", "/api/v1/remediation/execute", {"remediation_id": 1}),
    ("get", "/api/v1/remediation/pending", None),
])
def test_every_remediation_route_requires_a_token(client, method, path, body):
    call = getattr(client, method)
    response = call(path) if body is None else call(path, json=body)
    assert response.status_code in (401, 403), f"{path} answered {response.status_code}"


def test_a_forged_token_is_refused(client):
    response = client.get(
        "/api/v1/remediation/pending",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code in (401, 403)


# --------------------------------------------------------------------------
# The catalogue is the allow-list
# --------------------------------------------------------------------------

def test_actions_endpoint_publishes_the_contract(client):
    actions = client.get("/api/v1/remediation/actions", headers=auth(client)).json()["actions"]
    by_id = {a["action_id"]: a for a in actions}

    assert by_id["check_disk_space"]["read_only"] is True
    assert by_id["disable_startup_item"]["has_rollback"] is True
    assert by_id["clear_temp_files"]["has_rollback"] is False

    # The catalogue says plainly which actions cannot be confirmed, rather
    # than leaving a caller to find out afterwards. One action is in that
    # position today, and the test names it so that a second one cannot be
    # added quietly.
    unverifiable = sorted(a["action_id"] for a in actions if not a["verifiable"])
    assert unverifiable == ["restart_explorer"]


def test_an_unverifiable_action_is_never_reported_as_resolved(client):
    """``restart_explorer`` has no postcondition, so success cannot be shown.

    The system says inconclusive and escalates. That is the fail-closed
    direction, and it is the behaviour to defend rather than hide: the shell
    restarting leaves nothing observable that distinguishes a fix from a
    no-op.
    """
    headers = auth(client)
    proposal = medium_risk(client, headers, "restart_explorer", {}).json()
    token = approve(client, auth(client, USERS[1][0]), proposal["id"])

    body = execute(client, headers, proposal["id"], token).json()

    assert body["execution_result"]["success"] is True
    assert body["verification_status"] == "inconclusive"
    assert body["status"] == "escalated"


def test_an_action_with_no_contract_is_refused(client):
    headers = auth(client)
    response = propose(client, headers, action_id="format_c_drive")
    assert response.status_code == 400
    assert "contract" in response.json()["detail"]


def test_a_command_string_is_not_an_action(client):
    """The API takes an action id. A shell command is simply not in the
    catalogue, which is the whole point of the allow-list."""
    response = propose(client, auth(client), action_id="Remove-Item C:\\ -Recurse")
    assert response.status_code == 400


# --------------------------------------------------------------------------
# Propose and assess
# --------------------------------------------------------------------------

def test_proposing_scores_the_risk_and_runs_nothing(client, driver):
    before = driver.system.disk_free_gb
    body = propose(client, auth(client)).json()

    assert body["risk_level"] in ("low", "medium", "high")
    assert body["approval_route"]
    assert body["execution_result"] is None
    assert driver.system.disk_free_gb == before


def test_the_assessment_records_the_policy_version(client):
    """Every assessment carries the policy that produced it, so a score can be
    re-derived later (thesis 5.3.3)."""
    body = propose(client, auth(client)).json()
    assert body["risk_assessment"]["policy_version"]
    assert body["risk_assessment"]["weights"]


def test_weak_evidence_costs_autonomy(client):
    """The first claim of the research, end to end through the API.

    The same action, proposed twice with the same impact and scope, routes to
    a human when the knowledge-base match is poor.
    """
    headers = auth(client)
    strong = propose(client, headers).json()
    weak = propose(
        client, headers,
        evidence=[{"kb_id": "KB-007", "similarity_score": 0.31}],
        factors={
            "impact": 1,
            "confidence_rating": 1,
            "evidence_quality": 1,
            "irreversibility": 1,
            "affected_scope": 1,
        },
    ).json()

    assert strong["approval_route"] == "auto_candidate"
    assert weak["approval_route"] != "auto_candidate"
    assert weak["risk_score"] > strong["risk_score"]


# --------------------------------------------------------------------------
# Approval binding
# --------------------------------------------------------------------------

def test_a_medium_risk_action_cannot_run_without_approval(client, driver):
    headers = auth(client)
    proposal = medium_risk(client, headers, "disable_startup_item", {"item_name": "Spotify"}).json()
    assert proposal["approval_route"] == "user_approval"

    response = execute(client, headers, proposal["id"])
    assert response.status_code == 409
    assert driver.system.startup_items["Spotify"] is True


def test_approval_issues_a_token_and_execution_consumes_it(client):
    headers = auth(client)
    proposal = medium_risk(client, headers, "disable_startup_item", {"item_name": "Spotify"}).json()
    token = approve(client, auth(client, USERS[1][0]), proposal["id"])

    response = execute(client, headers, proposal["id"], token)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_a_token_cannot_be_used_twice(client):
    """TC07 through the API: one approval authorises one execution."""
    headers = auth(client)
    proposal = medium_risk(client, headers, "disable_startup_item", {"item_name": "Spotify"}).json()
    token = approve(client, auth(client, USERS[1][0]), proposal["id"])

    assert execute(client, headers, proposal["id"], token).status_code == 200
    assert execute(client, headers, proposal["id"], token).status_code == 409


def test_a_token_does_not_work_on_another_request(client):
    headers = auth(client)
    approver = auth(client, USERS[1][0])
    first = medium_risk(client, headers, "disable_startup_item", {"item_name": "Spotify"}).json()
    second = medium_risk(client, headers, "disable_startup_item", {"item_name": "OneDrive"}).json()

    stolen = approve(client, approver, first["id"])
    approve(client, approver, second["id"])

    assert execute(client, headers, second["id"], stolen).status_code == 409


def test_a_rejected_request_can_never_run(client, driver):
    headers = auth(client)
    proposal = medium_risk(client, headers, "disable_startup_item", {"item_name": "Spotify"}).json()

    rejected = client.post(
        "/api/v1/remediation/reject",
        json={"remediation_id": proposal["id"], "reason": "Not now, it is month end"},
        headers=auth(client, USERS[1][0]),
    )
    assert rejected.status_code == 200
    assert execute(client, headers, proposal["id"]).status_code == 409
    assert driver.system.startup_items["Spotify"] is True


def test_the_approver_is_taken_from_the_token_not_the_body(client):
    """A client cannot name someone else as the approver: the record would
    prove nothing if it could."""
    headers = auth(client)
    proposal = medium_risk(client, headers, "disable_startup_item", {"item_name": "Spotify"}).json()

    response = client.post(
        "/api/v1/remediation/approve",
        json={"remediation_id": proposal["id"], "approver_email": "ceo@acme-soft.com"},
        headers=auth(client, USERS[1][0]),
    )
    assert response.status_code == 200
    assert response.json()["approver_email"] == USERS[1][0]


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

def test_a_low_risk_action_runs_and_is_verified(client):
    headers = auth(client)
    proposal = propose(client, headers).json()
    assert proposal["approval_route"] == "auto_candidate"

    body = execute(client, headers, proposal["id"]).json()
    assert body["status"] == "completed"
    assert body["verification_status"] == "verified_success"


def test_a_silent_failure_is_never_reported_as_resolved(client, driver):
    """TC08 through the API: the command succeeds, the problem remains."""
    driver.inject_fault("clear_temp_files")
    headers = auth(client)
    proposal = propose(client, headers).json()

    body = execute(client, headers, proposal["id"]).json()

    assert body["execution_result"]["success"] is True
    assert body["verification_status"] == "verified_failure"
    assert body["status"] != "completed"
    assert body["status"] == "escalated"


def test_a_pre_check_failure_stops_the_action_being_run(client, driver):
    """TC06: the target does not exist, so nothing is attempted."""
    headers = auth(client)
    proposal = medium_risk(client, headers, "kill_process_by_id", {"pid": 999999}).json()
    token = approve(client, auth(client, USERS[1][0]), proposal["id"])

    body = execute(client, headers, proposal["id"], token).json()

    assert body["pre_check"]["status"] == "failed"
    assert body["execution_result"] is None
    assert body["status"] == "failed"


def test_a_read_only_diagnostic_needs_no_evidence(client):
    """Requiring evidence to read state would be circular: reading state is
    how evidence is gathered."""
    headers = auth(client)
    proposal = propose(client, headers, action_id="check_disk_space", evidence=[]).json()

    body = execute(client, headers, proposal["id"]).json()
    assert body["status"] == "completed"


# --------------------------------------------------------------------------
# Recovery
# --------------------------------------------------------------------------

def test_a_failed_remediation_rolls_back_and_verifies_the_rollback(client, driver):
    """Teams re-registers itself, so the disable completes and achieves nothing."""
    headers = auth(client)
    proposal = medium_risk(client, headers, "disable_startup_item", {"item_name": "Teams"}).json()
    token = approve(client, auth(client, USERS[1][0]), proposal["id"])

    body = execute(client, headers, proposal["id"], token).json()

    assert body["verification_status"] == "verified_failure"
    assert body["status"] == "rolled_back"
    assert body["rollback_result"]["verified"] is True
    assert driver.system.startup_items["Teams"] is True


def test_a_rollback_that_restores_nothing_escalates(client, driver):
    """Nothing was changed, so there is nothing saved to put back."""
    driver.inject_fault("disable_startup_item")
    headers = auth(client)
    proposal = medium_risk(client, headers, "disable_startup_item", {"item_name": "ScreenRecorder"}).json()
    token = approve(client, auth(client, USERS[1][0]), proposal["id"])

    body = execute(client, headers, proposal["id"], token).json()

    assert body["rollback_attempted"] is True
    assert body["rollback_result"]["verified"] is False
    assert body["status"] == "escalated"
    assert "manual attention" in body["escalation_reason"]


# --------------------------------------------------------------------------
# Who may see and do what
# --------------------------------------------------------------------------

def test_an_unrelated_user_cannot_execute_someone_elses_remediation(client, driver):
    owner = auth(client)
    proposal = propose(client, owner).json()

    response = execute(client, auth(client, USERS[2][0]), proposal["id"])

    assert response.status_code == 403
    assert driver.system.temp_files_mb > 0


def test_an_unrelated_user_cannot_read_someone_elses_remediation(client):
    proposal = propose(client, auth(client)).json()
    response = client.get(
        f"/api/v1/remediation/{proposal['id']}",
        headers=auth(client, USERS[2][0]),
    )
    assert response.status_code == 403


def test_support_staff_can_read_any_remediation(client):
    proposal = propose(client, auth(client)).json()
    response = client.get(
        f"/api/v1/remediation/{proposal['id']}",
        headers=auth(client, USERS[1][0]),
    )
    assert response.status_code == 200


def test_a_remediation_cannot_be_aimed_at_someone_elses_machine(client):
    response = propose(client, auth(client), device_id="dev_not_registered_here")
    assert response.status_code == 404


def test_a_missing_remediation_is_a_404_not_a_500(client):
    response = client.get("/api/v1/remediation/999999", headers=auth(client))
    assert response.status_code == 404


# --------------------------------------------------------------------------
# The trail
# --------------------------------------------------------------------------

def test_the_full_trail_is_retrievable_after_the_run(client):
    """Thesis 5 claims a record at every decision point. This is the endpoint
    a reviewer would actually open."""
    headers = auth(client)
    proposal = propose(client, headers).json()
    execute(client, headers, proposal["id"])

    trail = client.get(f"/api/v1/remediation/{proposal['id']}", headers=headers).json()

    assert trail["risk_assessment"]["factors"]
    assert trail["pre_check"]["status"] == "passed"
    assert trail["post_check"]["status"] == "verified_success"
    assert trail["execution_result"]["driver"] == "simulated"
    assert trail["evidence"][0]["kb_id"] == "KB-007"


def test_pending_lists_what_is_waiting_for_a_human(client):
    headers = auth(client)
    medium_risk(client, headers, "disable_startup_item", {"item_name": "Spotify"})

    pending = client.get("/api/v1/remediation/pending", headers=auth(client, USERS[1][0])).json()
    rows = pending if isinstance(pending, list) else pending.get("requests", pending.get("items", []))

    assert any(r["action_id"] == "disable_startup_item" for r in rows)
