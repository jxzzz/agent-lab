from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_requires_message():
    resp = client.post("/chat", json={"session_id": "test"})
    assert resp.status_code == 422


def test_chat_returns_answer(monkeypatch):
    def fake_ask(message: str, thread_id: str) -> str:
        return "这是测试回答"

    monkeypatch.setattr("api.ask", fake_ask)

    resp = client.post(
        "/chat",
        json={"message": "你好", "session_id": "test"},
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["answer"] == "这是测试回答"
    assert data["session_id"] == "test"
    assert data["request_id"]
    assert data["latency_ms"] >= 0
    
def test_chat_stream_returns_sse(monkeypatch):
    def fake_ask(message: str, thread_id: str) -> str:
        return "这是流式测试回答"

    monkeypatch.setattr("api.ask", fake_ask)

    with client.stream(
        "POST",
        "/chat/stream",
        json={"message": "你好", "session_id": "sse-test"},
    ) as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")

        body = "".join(resp.iter_text())

    assert "event: status" in body
    assert "event: answer" in body
    assert "这是流式测试回答" in body
    assert "event: done" in body