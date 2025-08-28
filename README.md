# OpenAI API Agent School - Project

본 자료는 [(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI API로 배우는 Agent 개발 첫걸음** ](https://openai-api-agent.aicastle.school/)(OpenAI API Agent School) 강의 프로젝트 자료입니다.


## [1] Agent 앱 실행하기

### 환경 설정

1. **.env** (필수)
    ```
    OPENAI_API_KEY=sk-proj-....
    PROMPT_ID=pmpt_....
    APP_TITLE="OpneAI API Agent School"
    ```
    - .env 파일을 생성하고 위와 같이 `OPENAI_API_KEY`, `PROMPT_ID`, `APP_TITLE`를 입력합니다.
    - **(주의) .gitignore에서 .env를 반드시 포함시켜 레포지토리에 푸시되지 않게 해야 합니다.**
1. **prompt_variables.yaml** (옵션)
    - 프롬프트에 변수가 포함된 경우 이 파일에 값을 입력합니다.
    - **(주의) 민감한 정보가 포함된 경우 절대 레포지토리를 공개하지 마세요**
1. **prompt_tools.py**
    - 이곳에 정의된 `tools=[...]`를 프롬프트에 정의된 툴에 덮어씁니다.
    - **(주의) mcp와 같이 Access Token 및 API KEY와 같은 민감한 값이 포함된 경우 절대 레포지토리를 공개하거나 prompt_tools.py를 푸시하면 안됩니다**

### Build Command
```sh
uv sync --frozen && uv cache prune --ci
```

### Start Command
```sh
uv run gunicorn app:app --timeout 0
```

## [2] 파인 튜닝

### supervised
```sh
uv run fine_tuning/supervised/data_gen.py
```
- `fine_tuning/supervised/data.jsonl`파일 생성