from fastapi.testclient import TestClient

from app.main import app


def test_health_mock():
    r = TestClient(app).get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["llm"]["provider"] == "mock"
    assert body["llm"]["ok"] is True


def test_health_ollama_down(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:1")
    r = TestClient(app).get("/api/health")
    assert r.status_code == 200
    assert r.json()["llm"]["ok"] is False
