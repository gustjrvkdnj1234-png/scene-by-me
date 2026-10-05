# ROADMAP: 씬바이미 PoC

각 Phase는 클로드 코드에 아래 코드블럭을 그대로 붙여 넣어 요청한다.
한 번에 한 Phase씩, 완료 후 맥에서 실행 확인하고 다음으로 넘어간다.

---

## Phase 0. 프로젝트 뼈대

- [x] 폴더 구조, requirements.txt, .env.example, .gitignore
- [x] LLM 공통 클라이언트 (ollama / mock)
- [x] FastAPI 실행 + 헬스체크
- [x] README 실행법

```
CLAUDE.md, docs/PRD.md, docs/ARCHITECTURE.md, docs/ROADMAP.md 를 먼저 읽어줘.
그다음 ROADMAP의 Phase 0만 진행해줘.

- ARCHITECTURE의 폴더 구조대로 뼈대를 만들고, 아직 구현하지 않는 파일은 만들지 마.
- app/llm/ 에 generate, generate_json, embed 세 가지를 가진 공통 클라이언트를 만들고, LLM_PROVIDER=ollama | mock 으로 전환되게 해줘.
- mock은 Ollama 없이도 테스트가 돌도록 고정된 응답을 반환해야 해.
- FastAPI에 GET /api/health 를 만들고, LLM 연결 상태도 함께 반환해줘.
- README.md 에 맥북(M1)에서 처음 실행하는 방법을 처음부터 적어줘: Ollama 설치, 모델 pull, 가상환경, 패키지 설치, 서버 실행, 브라우저 주소.
- pytest 로 헬스체크와 mock 클라이언트 테스트를 작성하고 통과시켜줘.
- 끝나면 CLAUDE.md 의 "실행 명령" 섹션과 ROADMAP 체크박스를 갱신하고, 바뀐 내용을 한국어로 짧게 요약해줘.
```

---

## Phase 1. 메모 입력 (F1)

- [x] memos 테이블, 메모 저장·목록 API
- [x] TXT·PDF 업로드
- [x] 채팅형 메모 화면

```
CLAUDE.md 와 docs 문서를 읽고 ROADMAP Phase 1만 진행해줘.

- memos 테이블과 POST /api/memos, GET /api/memos, POST /api/memos/upload 를 만들어줘.
- local_date 는 Asia/Seoul 기준 날짜로 저장해줘.
- PDF는 pypdf로 텍스트를 추출하고, 빈 줄 기준으로 나눠 여러 메모로 저장해줘.
- app/static/ 에 채팅 형태의 메모 화면을 만들어줘. 입력창, 전송, 파일 업로드, 지난 메모 목록(날짜별 구분). 깔끔하고 차분한 디자인으로.
- GET /api/status 로 서로 다른 기록 일수와 3일 충족 여부를 반환해줘.
- 테스트 작성 후 통과, 문서 갱신, 변경 요약까지 해줘.
```

---

## Phase 2. 상황 추출 + 맥락 저장 (F2)

- [ ] 추출 프롬프트, extractions 저장
- [ ] 인물 동일인 처리
- [ ] ChromaDB 임베딩 저장
- [ ] 백그라운드 처리

```
CLAUDE.md 와 docs 문서를 읽고 ROADMAP Phase 2만 진행해줘.

- 메모 저장 후 BackgroundTasks 로 상황 추출을 실행해줘.
- app/prompts/extract.md 에 프롬프트를 만들고, 인물·장소·시기·감정·사건을 JSON으로 받아 Pydantic으로 검증해줘. 실패 시 1회 재시도 후 로그만 남겨.
- 인물 동일인 처리: "엄마", "어머니"처럼 같은 사람으로 보이는 이름은 기존 characters 의 aliases 로 합쳐줘. 확실하지 않으면 별도 인물로 둬.
- 메모를 bge-m3 로 임베딩해 ChromaDB 에 저장해줘.
- mock 클라이언트도 추출 결과를 그럴듯하게 반환하도록 확장해줘.
- 테스트, 문서 갱신, 변경 요약까지.
```

---

## Phase 3. 문체 학습 + 3일 미리보기 (F3)

- [ ] 문체 프로필
- [ ] 미리보기 API와 상태 패널

```
CLAUDE.md 와 docs 문서를 읽고 ROADMAP Phase 3만 진행해줘.

- style_profile: 평균 메모 길이, 반말/존댓말, 자주 쓰는 표현은 코드로 계산하고, 말투 특징 요약(tone_notes)만 LLM으로 만들어줘. 메모 5개마다 갱신.
- GET /api/preview: 지금까지의 인물, 장소, 감정과 AI가 만든 예고편 한 줄(로그라인)을 반환해줘.
- 메모 화면 옆에 상태 패널을 추가해줘. 기록 일수와 3일 진행도, 등장 인물, 예고편 한 줄, "첫 장면까지 N일" 표시.
- 테스트, 문서 갱신, 변경 요약까지.
```

---

## Phase 4. 맥락 엮기 + 장면화 (F4, F5)

- [ ] 이야기 줄기(thread) 생성·병합
- [ ] 장면 생성 (3일 충족 시)
- [ ] 각본 화면

```
CLAUDE.md 와 docs 문서를 읽고 ROADMAP Phase 4만 진행해줘.

- 새 메모가 추출되면 ChromaDB 로 유사 메모를 찾고, LLM이 기존 thread 에 붙일지 새 thread 를 만들지 판단하게 해줘.
- 3일 규칙을 충족한 경우에만, 변경된 thread 의 장면을 생성 또는 갱신해줘.
- 장면은 ARCHITECTURE 의 "각본 형식 규칙"을 따르고, 문체 프로필을 대사에 반영해줘. 메모에 없는 사건은 지어내지 마.
- 각 장면에 출처 메모 id 를 저장해줘.
- 각본 화면을 추가해줘: 장면 목록, 각 장면에서 출처 메모 펼쳐보기.
- 테스트, 문서 갱신, 변경 요약까지.
```

---

## Phase 5. 서사 성장 + 출력 (F6, F7)

- [ ] 막 구성, 복선·전환점·주제
- [ ] 수동 재구성
- [ ] Markdown 내보내기, 인쇄용 화면

```
CLAUDE.md 와 docs 문서를 읽고 ROADMAP Phase 5만 진행해줘.

- 장면이 3개 이상 바뀔 때마다 story 를 갱신해줘: 로그라인, 주제, 3막 구성(막별 장면 배치), 복선, 전환점. 입력은 장면 전문이 아니라 장면 요약만 사용해 소형 모델 부담을 줄여줘.
- story 는 버전으로 쌓아 이전 버전도 남겨줘.
- POST /api/story/rebuild 로 수동 재구성.
- 각본 화면을 막 → 장면 구조로 개선하고, 상단에 로그라인과 주제를 보여줘.
- GET /api/export/markdown 과 /print 인쇄용 화면을 만들어줘 (브라우저 인쇄로 PDF 저장, 시나리오 서식).
- 테스트, 문서 갱신, 변경 요약까지.
```

---

## Phase 6. 사용자 테스트 준비

- [ ] 샘플 메모 데이터로 3일 시뮬레이션
- [ ] 품질 점검 체크리스트

```
CLAUDE.md 와 docs 문서를 읽고 ROADMAP Phase 6만 진행해줘.

- scripts/seed_sample.py: 서로 다른 날짜 5일치의 가상 일상 메모 20개를 넣는 스크립트를 만들어줘.
- scripts/evaluate.py: 장면별로 출처 메모와 대조해 "메모에 없는 사실이 들어갔는지" LLM으로 점검하는 리포트를 만들어줘.
- docs/USER_TEST.md: 실사용자 테스트 진행 방법과 설문(만족도 5점 척도 포함)을 작성해줘.
- 문서 갱신, 변경 요약까지.
```
