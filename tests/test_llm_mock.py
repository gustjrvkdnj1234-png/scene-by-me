import pytest
from pydantic import BaseModel

from app.llm import get_client
from app.llm.client import LLMClient


class Extraction(BaseModel):
    characters: list[str]
    places: list[str]
    time_hint: str
    emotions: list[str]
    events: list[str]


class Wrong(BaseModel):
    nothing: int


def test_generate():
    assert get_client().generate("안녕")


def test_generate_json_valid():
    result = get_client().generate_json("JSON 으로 추출해줘", Extraction)
    assert result is not None and "나" in result.characters


def test_generate_json_invalid_returns_none():
    assert get_client().generate_json("JSON 으로 추출해줘", Wrong) is None


def test_embed_deterministic():
    c = get_client()
    assert c.embed("가") == c.embed("가")
    assert c.embed("가") != c.embed("나")


def test_unknown_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nope")
    with pytest.raises(ValueError):
        get_client()


def test_is_llm_client():
    assert isinstance(get_client(), LLMClient)
