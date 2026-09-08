import sqlite3
from pathlib import Path

import requests
from streamlit.testing.v1 import AppTest

from services import ai_router, telemetry


def configure_database(monkeypatch, tmp_path):
    path = tmp_path / "telemetry.sqlite3"
    monkeypatch.setenv("CAREERLENS_TELEMETRY_DB", str(path))
    return path


def http_error(status_code):
    response = requests.Response()
    response.status_code = status_code
    return requests.HTTPError(response=response)


def test_analysis_telemetry_stores_only_allowlisted_metadata(monkeypatch, tmp_path):
    path = configure_database(monkeypatch, tmp_path)
    telemetry.record_analysis(
        telemetry.new_trace_id(), True, 1234.5, 78, "application", 2, 3
    )
    with sqlite3.connect(path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(analyses)")}
        row = connection.execute("SELECT * FROM analyses").fetchone()
    assert columns == {
        "trace_id", "timestamp", "success", "processing_ms", "match_score",
        "route", "page_count", "redaction_count", "error_type",
    }
    assert row is not None
    database_bytes = path.read_bytes().lower()
    for forbidden in (b"resume_text", b"job_description", b"prompt",
                      b"model_response", b"api_key", b"email", b"phone", b"url"):
        assert forbidden not in database_bytes


def test_router_records_failed_and_successful_provider_attempts(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)
    def quota_failure(*args):
        raise http_error(429)

    def success(*args):
        return "valid"

    monkeypatch.setattr(ai_router, "PROVIDERS", [
        ("Limited", quota_failure), ("Healthy", success)
    ])
    monkeypatch.setattr(ai_router, "RETRY_BACKOFF_SECONDS", 0)
    with telemetry.trace_context("opaque-test-trace"):
        result = ai_router._generate_with_fallback("system", "user", 10, str)
    attempts = telemetry.query_rows(
        "SELECT trace_id, provider, success, http_status, error_type "
        "FROM provider_attempts ORDER BY id"
    )
    assert result == "valid"
    assert attempts == [
        {"trace_id": "opaque-test-trace", "provider": "Limited", "success": 0,
         "http_status": 429, "error_type": "quota"},
        {"trace_id": "opaque-test-trace", "provider": "Limited", "success": 0,
         "http_status": 429, "error_type": "quota"},
        {"trace_id": "opaque-test-trace", "provider": "Healthy", "success": 1,
         "http_status": None, "error_type": None},
    ]


def test_timeout_omits_exception_message(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)

    def timeout(*args):
        raise requests.Timeout("secret request content")

    monkeypatch.setattr(ai_router, "PROVIDERS", [("Slow", timeout)])
    monkeypatch.setattr(ai_router, "RETRY_BACKOFF_SECONDS", 0)
    try:
        ai_router._generate_with_fallback("private prompt", "private resume", 10, str)
    except RuntimeError:
        pass
    attempts = telemetry.query_rows(
        "SELECT error_type, http_status FROM provider_attempts"
    )
    assert attempts == [
        {"error_type": "timeout", "http_status": None},
        {"error_type": "timeout", "http_status": None},
    ]
    assert b"secret request content" not in telemetry.database_path().read_bytes()


def test_dashboard_queries_are_read_only(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)
    assert telemetry.query_rows("SELECT COUNT(*) AS count FROM analyses")[0]["count"] == 0
    try:
        telemetry.query_rows("DELETE FROM analyses")
    except ValueError as error:
        assert "read-only" in str(error)
    else:
        raise AssertionError("A mutating query was accepted")


def test_dashboard_tabs_render_with_match_score(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)
    monkeypatch.setenv("CAREERLENS_DASHBOARD_PASSWORD", "test-password")
    telemetry.record_analysis(
        "dashboard-test-trace", True, 750, 72, "application", 2, 3
    )

    dashboard_path = (
        Path(__file__).parents[1] / "pages" / "Monitoring_Evaluation.py"
    )
    dashboard = AppTest.from_file(dashboard_path)
    dashboard.run(timeout=10)
    assert not dashboard.exception

    dashboard.text_input[0].set_value("test-password")
    dashboard.button[0].click().run(timeout=10)

    assert not dashboard.exception
    assert [tab.label for tab in dashboard.tabs] == [
        "Monitoring",
        "Evaluation",
        "Recent Traces",
    ]


def test_missing_credentials_skip_provider_without_calling_it(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    called = False

    def provider(*args):
        nonlocal called
        called = True
        return "unexpected"

    monkeypatch.setattr(ai_router, "PROVIDERS", [("Gemini", provider)])
    try:
        ai_router._generate_with_fallback("system", "user", 10, str)
    except RuntimeError as error:
        assert "No CareerLens AI provider is configured" in str(error)
    else:
        raise AssertionError("An unconfigured provider was attempted")

    assert not called
    assert telemetry.query_rows(
        "SELECT provider, success, error_type FROM provider_attempts"
    ) == [{"provider": "Gemini", "success": 0,
           "error_type": "configuration_error"}]


def test_temporary_gemini_failure_succeeds_on_retry(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)
    monkeypatch.setenv("GOOGLE_API_KEY", "not-recorded-test-key")
    monkeypatch.setattr(ai_router, "RETRY_BACKOFF_SECONDS", 0)
    calls = 0

    def provider(*args):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise requests.ConnectionError("temporary connection failure")
        return "valid"

    monkeypatch.setattr(ai_router, "PROVIDERS", [("Gemini", provider)])
    assert ai_router._generate_with_fallback("system", "user", 10, str) == "valid"
    assert calls == 2
    assert telemetry.query_rows(
        "SELECT success, error_type FROM provider_attempts ORDER BY id"
    ) == [
        {"success": 0, "error_type": "connection_error"},
        {"success": 1, "error_type": None},
    ]
    assert b"not-recorded-test-key" not in telemetry.database_path().read_bytes()


def test_authentication_failure_is_not_retried(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)
    monkeypatch.setenv("GOOGLE_API_KEY", "invalid-test-key")
    calls = 0

    def provider(*args):
        nonlocal calls
        calls += 1
        raise http_error(401)

    monkeypatch.setattr(ai_router, "PROVIDERS", [("Gemini", provider)])
    try:
        ai_router._generate_with_fallback("system", "user", 10, str)
    except RuntimeError:
        pass

    assert calls == 1
    assert telemetry.query_rows(
        "SELECT http_status, error_type FROM provider_attempts"
    ) == [{"http_status": 401, "error_type": "authentication_error"}]


def test_fallback_uses_next_configured_provider(monkeypatch, tmp_path):
    configure_database(monkeypatch, tmp_path)
    monkeypatch.setenv("GOOGLE_API_KEY", "configured")
    monkeypatch.setenv("OPENROUTER_API_KEY", "configured")
    monkeypatch.setattr(ai_router, "RETRY_BACKOFF_SECONDS", 0)
    calls = []

    def gemini(*args):
        calls.append("Gemini")
        raise http_error(503)

    def openrouter(*args):
        calls.append("OpenRouter")
        return "fallback result"

    monkeypatch.setattr(ai_router, "PROVIDERS", [
        ("Gemini", gemini), ("OpenRouter", openrouter)
    ])
    assert ai_router._generate_with_fallback(
        "system", "user", 10, str
    ) == "fallback result"
    assert calls == ["Gemini", "Gemini", "OpenRouter"]
