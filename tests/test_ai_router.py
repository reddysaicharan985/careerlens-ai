import sqlite3

import pytest
import requests

from services import ai_router, telemetry


def _response_error(status):
    response = requests.Response()
    response.status_code = status
    return requests.HTTPError(response=response)


def _clear_provider_environment(monkeypatch):
    for names in ai_router.PROVIDER_REQUIREMENTS.values():
        for name in names:
            monkeypatch.delenv(name, raising=False)


def test_missing_credentials_skip_providers_and_explain_configuration(monkeypatch, tmp_path):
    _clear_provider_environment(monkeypatch)
    monkeypatch.setenv("CAREERLENS_TELEMETRY_DB", str(tmp_path / "telemetry.sqlite3"))
    called = []
    monkeypatch.setattr(
        ai_router,
        "PROVIDERS",
        [(name, lambda *args: called.append(name)) for name in ai_router.PROVIDER_REQUIREMENTS],
    )

    with pytest.raises(RuntimeError, match="No AI provider is configured"):
        ai_router.generate_text("private system prompt", "private resume")

    assert called == []
    rows = telemetry.query_rows(
        "SELECT provider, error_type FROM provider_attempts ORDER BY id"
    )
    assert len(rows) == 5
    assert {row["error_type"] for row in rows} == {"configuration_error"}


def test_temporary_failure_is_retried_once_then_succeeds(monkeypatch):
    calls = []

    def flaky(*args):
        calls.append(1)
        if len(calls) == 1:
            raise requests.ConnectionError("temporary")
        return "recovered"

    monkeypatch.setattr(ai_router, "PROVIDERS", [("TestProvider", flaky)])
    monkeypatch.setattr(ai_router.time, "sleep", lambda seconds: None)
    assert ai_router.generate_text("system", "user") == "recovered"
    assert len(calls) == 2


@pytest.mark.parametrize("status", [401, 403])
def test_authentication_and_authorization_failures_are_not_retried(monkeypatch, status):
    failed_calls = []

    def auth_failure(*args):
        failed_calls.append(1)
        raise _response_error(status)

    monkeypatch.setattr(
        ai_router,
        "PROVIDERS",
        [("Denied", auth_failure), ("Backup", lambda *args: "backup result")],
    )
    assert ai_router.generate_text("system", "user") == "backup result"
    assert len(failed_calls) == 1


def test_malformed_output_retries_then_falls_back(monkeypatch):
    malformed_calls = []

    def malformed(*args):
        malformed_calls.append(1)
        return "not JSON"

    monkeypatch.setattr(
        ai_router,
        "PROVIDERS",
        [("Malformed", malformed), ("Backup", lambda *args: '{"ok": true}')],
    )
    monkeypatch.setattr(ai_router.time, "sleep", lambda seconds: None)
    assert ai_router.generate_structured("system", "user", {}) == {"ok": True}
    assert len(malformed_calls) == 2


def test_telemetry_never_contains_credentials_or_content(monkeypatch, tmp_path):
    database = tmp_path / "telemetry.sqlite3"
    monkeypatch.setenv("CAREERLENS_TELEMETRY_DB", str(database))
    monkeypatch.setenv("CEREBRAS_API_KEY", "super-secret-api-key")
    monkeypatch.setattr(
        ai_router,
        "PROVIDERS",
        [("Cerebras", lambda *args: (_ for _ in ()).throw(
            requests.Timeout("private resume and job description")
        ))],
    )
    monkeypatch.setattr(ai_router.time, "sleep", lambda seconds: None)

    with pytest.raises(RuntimeError):
        ai_router.generate_text("private prompt", "private personal data")

    stored = database.read_bytes().lower()
    for forbidden in (
        b"super-secret-api-key", b"private resume", b"job description",
        b"private prompt", b"private personal data",
    ):
        assert forbidden not in stored
    with sqlite3.connect(database) as connection:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(provider_attempts)")
        }
    assert columns == {
        "id", "trace_id", "timestamp", "provider", "latency_ms", "success",
        "http_status", "error_type",
    }
