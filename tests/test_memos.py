import io
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.services import memo_service


@pytest.fixture
def db_session():
    from app import models  # noqa: F401

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        yield s


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_and_list(client):
    r = client.post("/api/memos", json={"content": "  오늘 엄마랑 통화했다  "})
    assert r.status_code == 201
    assert r.json()["content"] == "오늘 엄마랑 통화했다"
    assert r.json()["source"] == "chat"
    assert len(client.get("/api/memos").json()) == 1


def test_empty_memo_rejected(client):
    assert client.post("/api/memos", json={"content": ""}).status_code == 422
    assert client.post("/api/memos", json={"content": "   "}).status_code == 400


def test_local_date_is_seoul(db_session):
    # UTC 15:30 = 서울 다음날 00:30 → local_date 는 서울 기준이어야 한다
    from datetime import timezone
    from zoneinfo import ZoneInfo

    utc = datetime(2026, 1, 1, 15, 30, tzinfo=timezone.utc)
    seoul = utc.astimezone(ZoneInfo("Asia/Seoul")).replace(tzinfo=None)
    m = memo_service.add_memo(db_session, "새벽 메모", now=seoul)
    assert str(m.local_date) == "2026-01-02"


def test_status_three_days(client, db_session):
    assert client.get("/api/status").json() == {
        "memo_count": 0, "days": 0, "required_days": 3, "met": False, "days_left": 3}
    for d in (1, 1, 2):
        memo_service.add_memo(db_session, "메모", now=datetime(2026, 3, d, 10, 0))
    s = client.get("/api/status").json()
    assert (s["memo_count"], s["days"], s["met"], s["days_left"]) == (3, 2, False, 1)
    memo_service.add_memo(db_session, "메모", now=datetime(2026, 3, 3, 10, 0))
    s = client.get("/api/status").json()
    assert s["days"] == 3 and s["met"] is True and s["days_left"] == 0


def test_upload_txt_splits_paragraphs(client):
    data = "첫 번째 일화\n이어지는 줄\n\n두 번째 일화\n\n\n세 번째".encode("utf-8")
    r = client.post("/api/memos/upload", files={"file": ("a.txt", data)})
    assert r.status_code == 201
    assert r.json()["saved"] == 3
    assert r.json()["memos"][0]["source"] == "txt"
    assert r.json()["memos"][0]["content"] == "첫 번째 일화\n이어지는 줄"


def test_upload_txt_cp949(client):
    data = "오늘의 메모".encode("cp949")
    r = client.post("/api/memos/upload", files={"file": ("a.txt", data)})
    assert r.json()["memos"][0]["content"] == "오늘의 메모"


def test_upload_pdf(client, monkeypatch):
    # 빈 PDF 는 글이 없어 400
    buf = io.BytesIO()
    w = PdfWriter(); w.add_blank_page(100, 100); w.write(buf)
    assert client.post("/api/memos/upload", files={"file": ("a.pdf", buf.getvalue())}).status_code == 400
    # 텍스트 추출 결과를 빈 줄 기준으로 나누는지 확인
    monkeypatch.setattr(memo_service, "extract_pdf_text", lambda d: "하나\n\n둘\n\n셋")
    r = client.post("/api/memos/upload", files={"file": ("a.pdf", b"x")})
    assert r.json()["saved"] == 3 and r.json()["memos"][0]["source"] == "pdf"


def test_upload_bad_type_and_broken_pdf(client):
    assert client.post("/api/memos/upload", files={"file": ("a.exe", b"x")}).status_code == 400
    assert client.post("/api/memos/upload", files={"file": ("a.pdf", b"not a pdf")}).status_code == 400


def test_index_page(client):
    r = client.get("/")
    assert r.status_code == 200 and "씬바이미" in r.text
    assert client.get("/static/app.js").status_code == 200
