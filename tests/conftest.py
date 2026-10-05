import os

# 테스트는 항상 mock LLM 으로 실행한다
os.environ["LLM_PROVIDER"] = "mock"
