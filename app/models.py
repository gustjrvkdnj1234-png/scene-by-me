"""SQLAlchemy 모델."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Memo(Base):
    __tablename__ = "memos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(10), default="chat")  # chat / txt / pdf
    created_at: Mapped[datetime] = mapped_column(DateTime)  # Asia/Seoul 기준 시각
    local_date: Mapped[date] = mapped_column(Date, index=True)  # Asia/Seoul 기준 날짜
