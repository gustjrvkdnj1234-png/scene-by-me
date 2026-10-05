"""F1 메모 저장, 파일 파싱, 기록 일수 계산."""
import io
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from pypdf import PdfReader
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Memo

KST = ZoneInfo("Asia/Seoul")
REQUIRED_DAYS = 3
MAX_MEMO_LEN = 20000


def now_kst() -> datetime:
    """Asia/Seoul 현재 시각 (tz 정보 없이 저장)."""
    return datetime.now(KST).replace(tzinfo=None, microsecond=0)


def add_memo(db: Session, content: str, source: str = "chat", now: datetime | None = None) -> Memo:
    """메모 하나를 저장한다. local_date 는 Asia/Seoul 기준."""
    now = now or now_kst()
    memo = Memo(content=content.strip(), source=source, created_at=now, local_date=now.date())
    db.add(memo)
    db.commit()
    db.refresh(memo)
    return memo


def list_memos(db: Session) -> list[Memo]:
    """오래된 순으로 메모를 반환한다."""
    return list(db.scalars(select(Memo).order_by(Memo.created_at, Memo.id)))


def split_paragraphs(text: str) -> list[str]:
    """빈 줄 기준으로 나누고, 너무 긴 덩어리는 잘라 메모 길이 제한을 지킨다."""
    chunks: list[str] = []
    for part in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        part = part.strip()
        while len(part) > MAX_MEMO_LEN:
            chunks.append(part[:MAX_MEMO_LEN])
            part = part[MAX_MEMO_LEN:]
        if part:
            chunks.append(part)
    return chunks


def decode_text(data: bytes) -> str:
    """TXT 인코딩 추정: UTF-8 우선, 실패하면 CP949."""
    for enc in ("utf-8-sig", "cp949"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_pdf_text(data: bytes) -> str:
    """PDF 전체 텍스트를 페이지 순서대로 합친다."""
    reader = PdfReader(io.BytesIO(data))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def add_upload(db: Session, filename: str, data: bytes) -> list[Memo]:
    """TXT·PDF 를 문단별 메모로 저장한다. 지원하지 않는 형식이면 ValueError."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "txt":
        text, source = decode_text(data), "txt"
    elif ext == "pdf":
        try:
            text, source = extract_pdf_text(data), "pdf"
        except Exception as e:
            raise ValueError("PDF 를 읽을 수 없어요.") from e
    else:
        raise ValueError("TXT 또는 PDF 파일만 올릴 수 있어요.")
    chunks = split_paragraphs(text)
    if not chunks:
        raise ValueError("파일에서 읽을 수 있는 글이 없어요.")
    now = now_kst()
    memos = [Memo(content=c, source=source, created_at=now, local_date=now.date()) for c in chunks]
    db.add_all(memos)
    db.commit()
    for m in memos:
        db.refresh(m)
    return memos


def get_status(db: Session) -> dict:
    """기록 일수와 3일 규칙 충족 여부."""
    days = db.scalar(select(func.count(func.distinct(Memo.local_date)))) or 0
    count = db.scalar(select(func.count(Memo.id))) or 0
    return {
        "memo_count": count,
        "days": days,
        "required_days": REQUIRED_DAYS,
        "met": days >= REQUIRED_DAYS,
        "days_left": max(REQUIRED_DAYS - days, 0),
    }
