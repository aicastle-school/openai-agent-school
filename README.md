# OpenAI API Agent School

본 자료는 [**OpenAI API로 배우는 Agent 개발 첫걸음**](https://openai-api-agent.aicastle.school/) 프로젝트 자료입니다.

## Agent 멀티모달 웹앱

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