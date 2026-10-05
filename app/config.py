"""환경 설정(.env) 로딩."""
import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    ollama_host: str
    llm_model: str
    embed_model: str
    llm_timeout: float
    data_dir: Path


def get_settings() -> Settings:
    """호출 시점의 환경변수로 설정을 만든다 (테스트에서 교체 가능)."""
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "ollama").lower(),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        llm_model=os.getenv("LLM_MODEL", "exaone3.5:7.8b"),
        embed_model=os.getenv("EMBED_MODEL", "bge-m3"),
        llm_timeout=float(os.getenv("LLM_TIMEOUT", "120")),
        data_dir=Path(os.getenv("DATA_DIR", "data")),
    )
