"""Password-protected monitoring and evaluation dashboard."""

import hmac
import os

import pandas as pd
import streamlit as st

from services.telemetry import query_rows


st.set_page_config(page_title="CareerLens M&E", page_icon="📊", layout="wide")


def dashboard_password():
    value = os.getenv("CAREERLENS_DASHBOARD_PASSWORD", "")
    if value:
        return value
    try:
        return str(st.secrets.get("CAREERLENS_DASHBOARD_PASSWORD", ""))
    except (FileNotFoundError, KeyError):
        return ""


def authenticate():
    if st.session_state.get("dashboard_authenticated"):
        return True
    st.title("CareerLens Monitoring & Evaluation")
    configured = dashboard_password()
    if not configured:
        st.error("Dashboard access is disabled until a password is configured.")
        return False
    supplied = st.text_input("Dashboard password", type="password")
    if st.button("Sign in", type="primary"):
        if hmac.compare_digest(supplied, configured):
            st.session_state.dashboard_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


if not authenticate():
    st.stop()

st.title("CareerLens Monitoring & Evaluation")
st.caption("Privacy-safe operational metadata only — no resume or job content is stored.")

kpis = query_rows("""SELECT COUNT(*) AS total,
    COALESCE(100.0 * AVG(success), 0) AS success_rate,
    COALESCE(AVG(processing_ms), 0) AS avg_ms,
    COALESCE(AVG(match_score), 0) AS avg_score FROM analyses""")[0]
columns = st.columns(4)
columns[0].metric("Total analyses", kpis["total"])
columns[1].metric("Success rate", f'{kpis["success_rate"]:.1f}%')
columns[2].metric("Average processing time", f'{kpis["avg_ms"] / 1000:.2f}s')
columns[3].metric("Average match score", f'{kpis["avg_score"]:.1f}%')

monitoring, evaluation, traces = st.tabs(
    ["Monitoring", "Evaluation", "Recent Traces"]
)
with monitoring:
    providers = pd.DataFrame(query_rows("""SELECT provider,
        COUNT(*) AS attempts, ROUND(100.0 * AVG(success), 1) AS success_rate,
        ROUND(AVG(latency_ms), 1) AS avg_latency_ms,
        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) AS fallback_failures,
        SUM(CASE WHEN http_status = 429 THEN 1 ELSE 0 END) AS quota_429,
        SUM(CASE WHEN error_type = 'timeout' THEN 1 ELSE 0 END) AS timeouts
        FROM provider_attempts GROUP BY provider ORDER BY attempts DESC"""))
    if providers.empty:
        st.info("No provider attempts recorded yet.")
    else:
        st.dataframe(providers, use_container_width=True, hide_index=True)
        st.bar_chart(providers.set_index("provider")[["attempts", "fallback_failures"]])
        st.bar_chart(providers.set_index("provider")[["avg_latency_ms"]])

with evaluation:
    scores = pd.DataFrame(query_rows(
        "SELECT match_score FROM analyses WHERE match_score IS NOT NULL"
    ))
    routes = pd.DataFrame(query_rows("""SELECT route, COUNT(*) AS analyses
        FROM analyses WHERE route != 'unknown' GROUP BY route"""))
    redactions = query_rows("""SELECT COUNT(*) AS runs_with_redactions,
        COALESCE(SUM(redaction_count), 0) AS total_redactions,
        COALESCE(AVG(redaction_count), 0) AS avg_redactions
        FROM analyses WHERE redaction_count > 0""")[0]
    left, right = st.columns(2)
    with left:
        st.subheader("Match-score distribution")
        if scores.empty:
            st.info("No scores recorded yet.")
        else:
            bins = pd.cut(scores["match_score"], bins=[0, 20, 40, 60, 80, 100],
                          include_lowest=True).value_counts(sort=False)
            st.bar_chart(bins)
    with right:
        st.subheader("Routing decisions")
        if routes.empty:
            st.info("No routing decisions recorded yet.")
        else:
            st.bar_chart(routes.set_index("route"))
    st.subheader("Privacy-redaction signals")
    redaction_columns = st.columns(3)
    redaction_columns[0].metric("Runs with redactions", redactions["runs_with_redactions"])
    redaction_columns[1].metric("Total redactions", redactions["total_redactions"])
    redaction_columns[2].metric("Average per affected run", f'{redactions["avg_redactions"]:.1f}')

with traces:
    recent = pd.DataFrame(query_rows("""SELECT substr(trace_id, 1, 12) AS trace_id,
        timestamp, success, ROUND(processing_ms, 1) AS latency_ms, match_score,
        route, page_count, redaction_count, error_type
        FROM analyses ORDER BY timestamp DESC LIMIT 100"""))
    if recent.empty:
        st.info("No traces recorded yet.")
    else:
        recent["success"] = recent["success"].astype(bool)
        st.dataframe(recent, use_container_width=True, hide_index=True)
