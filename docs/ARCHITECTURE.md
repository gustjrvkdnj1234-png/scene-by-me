# ARCHITECTURE: 씬바이미 PoC

## 하드웨어 예산 (M1 Pro, 16GB)

| 구성 | 메모리 |
|---|---|
| LLM `exaone3.5:7.8b` (Q4) | 약 5GB |
| 임베딩 `bge-m3` | 약 1.2GB |
| Python 서버 + ChromaDB | 약 1GB |
| 합계 | 약 7~8GB (여유 있음) |

- 7~8B 모델은 추출·분류는 안정적이나, 긴 각본 생성 품질은 한계가 있다.
- 따라서 각본 생성은 "장면 하나씩" 작게 나눠 호출하고, 전체 구조 갱신은 요약본만 입력한다.
- 모델은 `.env`의 `LLM_MODEL`로 교체 가능해야 한다.

## 폴더 구조

```
scene-by-me/
├─ CLAUDE.md
├─ README.md
├─ requirements.txt
├─ .env.example
├─ docs/
├─ app/
│  ├─ main.py              # FastAPI 진입점
│  ├─ config.py            # .env 설정 로딩
│  ├─ db.py                # SQLite 연결
│  ├─ models.py            # SQLAlchemy 모델
│  ├─ schemas.py           # Pydantic 스키마 (API + LLM 출력 검증)
│  ├─ llm/
│  │  ├─ client.py         # 공통 인터페이스 (generate, generate_json, embed)
│  │  ├─ ollama_client.py
│  │  └─ mock_client.py
│  ├─ prompts/             # 프롬프트 .md 파일
│  ├─ services/
│  │  ├─ memo_service.py      # F1 메모 저장, 파일 파싱
│  │  ├─ extract_service.py   # F2 상황 추출
│  │  ├─ entity_service.py    # 인물 동일인 처리
│  │  ├─ style_service.py     # F3 문체 프로필
│  │  ├─ thread_service.py    # F4 맥락 엮기
│  │  ├─ scene_service.py     # F5 장면화
│  │  ├─ story_service.py     # F6 서사 성장
│  │  └─ export_service.py    # F7 내보내기
│  ├─ vector_store.py      # ChromaDB 래퍼
│  └─ static/              # index.html, app.js, style.css
├─ data/                   # git 제외 (SQLite, Chroma, 업로드 파일)
└─ tests/
```

## 데이터 모델 (SQLite)

| 테이블 | 주요 컬럼 |
|---|---|
| memos | id, content, source(chat/txt/pdf), created_at, local_date |
| extractions | id, memo_id, characters(JSON), places(JSON), time_hint, emotions(JSON), events(JSON) |
| characters | id, name, aliases(JSON), first_seen_memo_id, mention_count |
| threads | id, title, summary, theme, memo_ids(JSON), updated_at |
| scenes | id, thread_id, heading, action, dialogue(JSON), source_memo_ids(JSON), order_index, created_at |
| story | id, version, logline, themes(JSON), acts(JSON: 막별 scene_id 목록), foreshadowing(JSON), turning_points(JSON), updated_at |
| style_profile | id, avg_length, speech_level, frequent_expressions(JSON), tone_notes, updated_at |

ChromaDB 컬렉션: `memos` (메모 임베딩, metadata에 memo_id, local_date)

## 처리 파이프라인

```
메모 입력
 ├─ 1. 저장 (memos)
 ├─ 2. 상황 추출 → extractions          [LLM JSON]
 ├─ 3. 인물 동일인 처리 → characters    [규칙 + LLM 판단]
 ├─ 4. 임베딩 → ChromaDB
 ├─ 5. 문체 프로필 갱신 (메모 5개마다)   [통계 + LLM]
 ├─ 6. 맥락 엮기: 유사 메모 검색 → 기존 thread에 추가 or 새 thread 생성  [LLM]
 └─ 7. 3일 규칙 확인
       ├─ 미충족 → 미리보기 갱신 (인물, 감정, 예고편 한 줄)
       └─ 충족 → 변경된 thread의 장면 생성/갱신 → 서사 구조 갱신 (N개 장면 변경 시)
```

- 2~7단계는 메모 저장 후 백그라운드 작업(FastAPI BackgroundTasks)으로 처리. 사용자는 기다리지 않는다.
- 각 단계 실패는 로그만 남기고 다음 메모 처리에 영향 주지 않는다.

## API

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | /api/memos | 메모 저장 |
| GET | /api/memos | 메모 목록 |
| POST | /api/memos/upload | TXT·PDF 업로드 |
| GET | /api/status | 기록 일수, 3일 충족 여부, 처리 대기 수 |
| GET | /api/preview | 인물, 장소, 감정, 예고편 한 줄 |
| GET | /api/story | 막·장면 전체 각본 |
| POST | /api/story/rebuild | 각본 전체 재구성 (수동) |
| GET | /api/export/markdown | Markdown 다운로드 |
| GET | /print | 인쇄용 각본 화면 (브라우저 인쇄로 PDF 저장) |

## 각본 형식 규칙

- 씬 헤딩: `S#번호. 장소 - 시간대` (예: `S#3. 회사 옥상 - 밤`)
- 지문: 현재형, 짧은 문장
- 대사: `인물명: 대사` 형태, 사용자 문체 프로필 반영
- 사용자 본인은 기본 이름 "나" (설정에서 변경 가능하도록 확장 여지만 둔다)
- 메모에 없는 사건을 지어내지 않는다. 연결과 각색은 하되, 사실 날조는 금지.
