"""FastAPI 진입점."""
from fastapi import FastAPI

from app.llm import get_client

app = FastAPI(title="Scene by Me (씬바이미)")


@app.get("/api/health")
def health() -> dict:
    """서버 상태와 LLM 연결 상태를 반환한다."""
    try:
        llm = get_client().health()
    except Exception as e:
        llm = {"ok": False, "detail": str(e)}
    return {"status": "ok", "llm": llm}
