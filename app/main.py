"""FastAPI 진입점."""
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.db import get_db
from app.llm import get_client
from app.schemas import MemoCreate, MemoOut, StatusOut, UploadOut
from app.services import memo_service

STATIC_DIR = Path(__file__).parent / "static"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(title="Scene by Me (씬바이미)")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """메모 화면."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    """서버 상태와 LLM 연결 상태를 반환한다."""
    try:
        llm = get_client().health()
    except Exception as e:
        llm = {"ok": False, "detail": str(e)}
    return {"status": "ok", "llm": llm}


@app.post("/api/memos", response_model=MemoOut, status_code=201)
def create_memo(body: MemoCreate, db: Session = Depends(get_db)):
    if not body.content.strip():
        raise HTTPException(400, "메모 내용이 비어 있어요.")
    return memo_service.add_memo(db, body.content)


@app.get("/api/memos", response_model=list[MemoOut])
def list_memos(db: Session = Depends(get_db)):
    return memo_service.list_memos(db)


@app.post("/api/memos/upload", response_model=UploadOut, status_code=201)
async def upload_memos(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "파일은 10MB 이하만 올릴 수 있어요.")
    try:
        memos = memo_service.add_upload(db, file.filename or "", data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"saved": len(memos), "memos": memos}


@app.get("/api/status", response_model=StatusOut)
def status(db: Session = Depends(get_db)):
    return memo_service.get_status(db)
