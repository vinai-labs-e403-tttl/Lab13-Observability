from __future__ import annotations

from fastapi.testclient import TestClient

from app.agent import AgentResult, LabAgent
from app.main import app
from app.pii import hash_user_id


class TraceContextSpy:
    def __init__(self) -> None:
        self.trace_kwargs: dict | None = None
        self.observation_kwargs: dict | None = None

    def update_current_trace(self, **kwargs) -> None:
        self.trace_kwargs = kwargs

    def update_current_observation(self, **kwargs) -> None:
        self.observation_kwargs = kwargs


def test_lab_agent_run_updates_langfuse_trace_tags_and_metadata(monkeypatch) -> None:
    agent = LabAgent(model="trace-test-model")
    trace_spy = TraceContextSpy()
    recorded_metrics: dict | None = None

    class FakeResponse:
        text = "Monitoring starts with traces and logs."
        usage = type("Usage", (), {"input_tokens": 42, "output_tokens": 84})()

    def fake_record_request(**kwargs) -> None:
        nonlocal recorded_metrics
        recorded_metrics = kwargs

    monkeypatch.setattr("app.agent.retrieve", lambda _: ["doc-a", "doc-b", "doc-c"])
    monkeypatch.setattr(agent.llm, "generate", lambda prompt: FakeResponse())
    monkeypatch.setattr("app.agent.langfuse_context", trace_spy)
    monkeypatch.setattr("app.agent.metrics.record_request", fake_record_request)

    result = agent.run(
        user_id="u_trace_01",
        feature="summary",
        session_id="s_trace_01",
        message="Summarize monitoring benefits for student@vinuni.edu.vn",
    )

    assert result.answer == FakeResponse.text
    assert trace_spy.trace_kwargs == {
        "user_id": hash_user_id("u_trace_01"),
        "session_id": "s_trace_01",
        "tags": ["lab", "summary", "trace-test-model"],
    }
    assert trace_spy.observation_kwargs == {
        "metadata": {
            "doc_count": 3,
            "query_preview": "Summarize monitoring benefits for [REDACTED_EMAIL]",
        },
        "usage_details": {"input": 42, "output": 84},
    }
    assert recorded_metrics is not None
    assert recorded_metrics["tokens_in"] == 42
    assert recorded_metrics["tokens_out"] == 84


def test_chat_requests_use_agent_run_and_return_correlation_id(monkeypatch) -> None:
    captured: dict | None = None

    def fake_run(*, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        nonlocal captured
        captured = {
            "user_id": user_id,
            "feature": feature,
            "session_id": session_id,
            "message": message,
        }
        return AgentResult(
            answer="ok",
            latency_ms=123,
            tokens_in=10,
            tokens_out=20,
            cost_usd=0.001,
            quality_score=0.9,
        )

    monkeypatch.setattr("app.main.agent.run", fake_run)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "req-trace123"},
            json={
                "user_id": "u_trace_02",
                "session_id": "s_trace_02",
                "feature": "qa",
                "message": "What do traces help diagnose?",
            },
        )

    assert response.status_code == 200
    assert captured == {
        "user_id": "u_trace_02",
        "feature": "qa",
        "session_id": "s_trace_02",
        "message": "What do traces help diagnose?",
    }
    assert response.json()["correlation_id"] == "req-trace123"
    assert response.headers["x-request-id"] == "req-trace123"
