# OpenAI API Agent Project

본 자료는 [(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI API로 배우는 Agent 개발 첫걸음** ](https://openai-api-agent.aicastle.school/)(OpenAI API Agent School) 강의 프로젝트 자료입니다.


## Agent 멀티모달 웹앱

### 환경변수 설정

1. `.env`파일을 생성하고 아래와 같은 양식으로 작성
    ```
    OPENAI_API_KEY=sk-proj-....
    PROMPT_ID=pmpt_....
    APP_TITLE="OpneAI API Agent School"
    ```
1. `prompt_variables.yaml` (옵션): 프롬프트 변수 정의
1. `tools.py` (옵션): 사용자 정의 툴을 작성
    - 프롬프트에 정의된 툴이 덮어씌워집니다.
    - **mcp 툴과 같은 민감한 값이 정의되어 있는 경우 절대 레포지토리를 공개로 배포해서는 안됩니다.**

### Build Command
```sh
uv sync --frozen && uv cache prune --ci
```

### Start Command
```sh
uv run gunicorn app:app --timeout 0
```

## 파인 튜닝

### supervised
```sh
uv run fine_tuning/supervised/data_gen.py
```
- `fine_tuning/supervised/data.jsonl`파일 생성