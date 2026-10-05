"""API 스키마."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoCreate(BaseModel):
    content: str = Field(min_length=1, max_length=20000)


class MemoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    source: str
    created_at: datetime
    local_date: date


class StatusOut(BaseModel):
    memo_count: int
    days: int  # 서로 다른 기록 날짜 수
    required_days: int
    met: bool  # 3일 규칙 충족 여부
    days_left: int  # 첫 장면까지 남은 일수


class UploadOut(BaseModel):
    saved: int
    memos: list[MemoOut]
