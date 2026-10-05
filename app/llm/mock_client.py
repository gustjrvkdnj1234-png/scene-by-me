"""Ollama 없이 동작하는 고정 응답 클라이언트 (테스트·개발용)."""
import hashlib
import json

from app.llm.client import LLMClient

MOCK_TEXT = "퇴근길에 오래된 친구에게서 연락이 왔다. 나는 잠시 망설이다 전화를 받는다."
MOCK_JSON = {
    "characters": ["나", "친구"],
    "places": ["퇴근길"],
    "time_hint": "저녁",
    "emotions": ["반가움", "망설임"],
    "events": ["오랜만에 친구에게 연락이 왔다"],
}


class MockClient(LLMClient):
    name = "mock"

    def generate(self, prompt: str, system: str | None = None) -> str:
        # JSON 을 요청하는 프롬프트에는 JSON 문자열을 돌려준다
        if "JSON" in prompt or "json" in prompt:
            return json.dumps(MOCK_JSON, ensure_ascii=False)
        return MOCK_TEXT

    def embed(self, text: str) -> list[float]:
        """같은 텍스트는 항상 같은 8차원 벡터를 반환한다."""
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [b / 255 for b in digest[:8]]

    def health(self) -> dict:
        return {"provider": self.name, "ok": True, "model": "mock", "detail": "mock 모드 (Ollama 불필요)"}
