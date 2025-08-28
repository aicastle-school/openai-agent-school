# OpenAI API Agent Project

본 자료는 [**OpenAI API로 배우는 Agent 개발 첫걸음**](https://openai-api-agent.aicastle.school/) 프로젝트 자료입니다.

## Agent 멀티모달 웹앱

### 환경변수 설정

`.env`파일을 생성하고 아래와 같은 양식으로 작성

```
OPENAI_API_KEY=sk-proj-....
PROMPT_ID=pmpt_....
APP_TITLE="OpneAI API Agent School"
```

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