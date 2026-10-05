# Scene by Me (씬바이미)

흘려 쓴 메모가 쌓이면 AI가 상황을 엮어 한 편의 각본으로 만들어주는 서비스 (PoC).
기획·구조·진행 단계는 `docs/` 를 참고하세요.

## 처음 실행하기 (맥북 M1)

### 1. Homebrew, Python 3.11, Ollama 설치
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11 ollama
brew services start ollama      # Ollama 를 백그라운드로 실행
```

### 2. 모델 받기 (약 6GB, 한 번만)
```bash
ollama pull exaone3.5:7.8b      # 대화·각본 생성용
ollama pull bge-m3              # 임베딩용
```

### 3. 가상환경과 패키지
```bash
cd scene-by-me
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # 필요하면 LLM_MODEL 등을 수정
```

### 4. 서버 실행
```bash
uvicorn app.main:app --reload
```
브라우저에서 http://127.0.0.1:8000 을 열면 메모 화면이 나옵니다.
- 메모 입력: Enter 전송, Shift+Enter 줄바꿈. TXT·PDF 는 '파일 올리기'로 올리면 빈 줄 기준 문단별로 저장됩니다.
- 서버·LLM 상태: http://127.0.0.1:8000/api/health
- 기록 일수·3일 충족 여부: http://127.0.0.1:8000/api/status
- 메모는 `data/scene.db` (SQLite)에 저장되며 git 에는 올라가지 않습니다. 날짜는 Asia/Seoul 기준입니다.
(자동 API 문서: http://127.0.0.1:8000/docs)

### Ollama 없이 실행 (mock)
`.env` 에서 `LLM_PROVIDER=mock` 으로 바꾸면 고정 응답으로 전체가 동작합니다.

## 테스트
```bash
pytest          # 항상 mock LLM 으로 실행되어 Ollama 가 필요 없습니다
```

## 설정 (.env)
| 키 | 기본값 | 설명 |
|---|---|---|
| LLM_PROVIDER | ollama | `ollama` 또는 `mock` |
| LLM_MODEL | exaone3.5:7.8b | 대안: `qwen2.5:7b` |
| EMBED_MODEL | bge-m3 | 임베딩 모델 |
| DATA_DIR | data | 메모 DB 저장 폴더 |
| OLLAMA_HOST | http://localhost:11434 | Ollama 주소 |
