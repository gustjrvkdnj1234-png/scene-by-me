# Scene by Me (씬바이미)

흘려 쓴 메모가 쌓이면 AI가 상황을 엮어, 평범한 일상을 한 편의 각본으로 만들어주는 서비스. 현재 PoC 단계.

- 기획: `docs/PRD.md`
- 구조: `docs/ARCHITECTURE.md`
- 진행 단계: `docs/ROADMAP.md`

작업 전 위 세 문서를 반드시 먼저 읽을 것.

## 운영자 정보

- 운영자는 연극영화 전공, AI 개발자. 코드 전문가는 아니므로 변경 사항은 "무엇을, 왜" 바꿨는지 한국어로 짧게 설명할 것.
- 실행 환경: MacBook M1 Pro, RAM 16GB, Python 3.11
- 작업 방식: Claude Code(웹)에서 개발 → GitHub 반영 → 로컬 맥에서 pull 후 실행
- 따라서 웹 샌드박스에는 Ollama가 없다. 테스트는 mock LLM으로 돌아가야 한다.

## 기술 스택

- 백엔드: FastAPI
- 프론트엔드: FastAPI가 서빙하는 단일 HTML + 바닐라 JS (빌드 도구 없음)
- LLM: Ollama 로컬 모델 (기본 `exaone3.5:7.8b`, 대안 `qwen2.5:7b`), `.env`로 교체 가능
- 임베딩: Ollama `bge-m3`
- 저장소: SQLite (SQLAlchemy) + ChromaDB (로컬 영구 저장)
- 파일 파싱: TXT, PDF (`pypdf`)
- 테스트: pytest

## 핵심 규칙

1. 모든 LLM·임베딩 호출은 `app/llm/` 공통 클라이언트를 통해서만 한다. 다른 곳에서 직접 호출 금지.
2. `LLM_PROVIDER=ollama | mock` 를 지원한다. mock은 고정된 그럴듯한 응답을 반환해 Ollama 없이도 전체 흐름과 테스트가 동작해야 한다.
3. LLM이 구조화 데이터를 반환할 때는 Pydantic 스키마로 검증한다. 실패 시 1회 재시도 후 로그를 남기고 건너뛴다 (서비스는 멈추지 않는다).
4. 프롬프트는 `app/prompts/*.md` 파일로 분리한다. 코드에 하드코딩 금지.
5. 사용자 데이터 폴더 `data/` 와 `.env` 는 git에 올리지 않는다.
6. 한 번에 ROADMAP의 Phase 하나만 작업한다. 범위 밖 기능을 미리 만들지 않는다.
7. 작업 완료 조건: `pytest` 통과, `README.md` 실행법 갱신, ROADMAP 체크박스 갱신.

## 코드 스타일

- 타입 힌트 사용, docstring과 주석은 한국어
- UI 문구는 한국어
- 파일 하나가 300줄을 넘으면 분리를 고려

## 실행 명령

Phase 0 완료 후 여기에 실제 명령을 기록할 것.
