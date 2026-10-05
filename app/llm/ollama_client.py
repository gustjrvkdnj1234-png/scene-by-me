"""Ollama 로컬 서버 클라이언트."""
import httpx

from app.llm.client import LLMClient


class OllamaClient(LLMClient):
    name = "ollama"

    def __init__(self, host: str, model: str, embed_model: str, timeout: float = 120) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.embed_model = embed_model
        self.timeout = timeout

    def generate(self, prompt: str, system: str | None = None) -> str:
        body = {"model": self.model, "prompt": prompt, "stream": False}
        if system:
            body["system"] = system
        r = httpx.post(f"{self.host}/api/generate", json=body, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["response"]

    def embed(self, text: str) -> list[float]:
        r = httpx.post(
            f"{self.host}/api/embed",
            json={"model": self.embed_model, "input": text},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()["embeddings"][0]

    def health(self) -> dict:
        """Ollama 서버 응답 여부와 필요한 모델 설치 여부를 확인한다."""
        try:
            r = httpx.get(f"{self.host}/api/tags", timeout=3)
            r.raise_for_status()
        except Exception as e:
            return {"provider": self.name, "ok": False, "model": self.model, "detail": f"Ollama 연결 실패: {e}"}
        installed = {m["name"] for m in r.json().get("models", [])}
        has = lambda n: n in installed or f"{n}:latest" in installed
        missing = [n for n in (self.model, self.embed_model) if not has(n)]
        if missing:
            return {"provider": self.name, "ok": False, "model": self.model,
                    "detail": f"모델 미설치: {', '.join(missing)} (ollama pull 필요)"}
        return {"provider": self.name, "ok": True, "model": self.model, "detail": "연결됨"}
