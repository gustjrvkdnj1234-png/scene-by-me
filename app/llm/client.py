"""LLM 공통 인터페이스. 모든 LLM·임베딩 호출은 여기를 통해서만 한다."""
import json
import logging
from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.config import get_settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMClient(ABC):
    """generate / embed / health 를 구현하면 generate_json 은 공통으로 제공된다."""

    name: str = "base"

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None) -> str:
        """텍스트 생성."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """임베딩 벡터 반환."""

    @abstractmethod
    def health(self) -> dict:
        """연결 상태 반환: {provider, ok, model, detail}."""

    def generate_json(self, prompt: str, schema: type[T], system: str | None = None) -> T | None:
        """JSON 생성 후 Pydantic 검증. 실패 시 1회 재시도, 그래도 실패하면 로그만 남기고 None."""
        for attempt in (1, 2):
            try:
                raw = self.generate(prompt, system=system)
                return schema.model_validate(json.loads(_extract_json(raw)))
            except (ValueError, ValidationError) as e:
                logger.warning("JSON 검증 실패 (%d/2): %s", attempt, e)
            except Exception as e:  # 네트워크 등 — 서비스는 멈추지 않는다
                logger.warning("LLM 호출 실패 (%d/2): %s", attempt, e)
        logger.error("generate_json 최종 실패, 건너뜀 (schema=%s)", schema.__name__)
        return None


def _extract_json(text: str) -> str:
    """응답에서 첫 '{' 부터 마지막 '}' 까지를 잘라낸다 (코드펜스 등 제거)."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("JSON 객체를 찾을 수 없음")
    return text[start : end + 1]


def get_client() -> LLMClient:
    """LLM_PROVIDER 설정에 맞는 클라이언트를 반환한다."""
    s = get_settings()
    if s.llm_provider == "mock":
        from app.llm.mock_client import MockClient

        return MockClient()
    if s.llm_provider == "ollama":
        from app.llm.ollama_client import OllamaClient

        return OllamaClient(s.ollama_host, s.llm_model, s.embed_model, s.llm_timeout)
    raise ValueError(f"지원하지 않는 LLM_PROVIDER: {s.llm_provider}")
