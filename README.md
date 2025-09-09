# OpenAI API Agent School - Project

본 자료는 [(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI API로 배우는 Agent 개발 첫걸음** ](https://openai-api-agent.aicastle.school/)(OpenAI API Agent School) 강의 프로젝트 자료입니다.


## [1] Agent 앱

### 1.1. 프로젝트 세팅

#### 환경 변수 (필수)

- 아래와 같은 환경변수를 .env 파일에 설정 또는 배포 환경에서 등록
- 셈플: [.env.example](.env.example)

```
OPENAI_API_KEY="sk-proj-........"
PROMPT_ID="pmpt_........"
TITLE="🤖 OpenAI API Agent School"
PASSWORD=""
```
> `OPENAI_API_KEY`: OpenAI API키를 설정  
> `PROMPT_ID` (옵션): OpenAI 대시보드에서 프롬프트 ID 입력  
> `TITLE` (옵션): 실행 될 앱의 상단 제목  
> `PASSWORD` (옵션): 비밀번호가 설정된 앱을 원할경우 입력

#### config.overrides.jsonc (선택)

- openai responses api 요청시 덮어쓸 파라미터가 있다면 config.overrides.jsonc에 정의.
- 파일 위치: /etc/secrets/ (우선) 또는 프로젝트 폴더
- 셈플: [config.overrides.jsonc.example](config.overrides.jsonc.example)

#### function_call.py (선택)

- function_call에서 사용할 함수를 [function_call.py](function_call.py)에 작성.

### 1.2. 앱 실행

#### Build Command
```sh
uv sync --frozen && uv cache prune --ci
```

#### Start Command
```sh
uv run gunicorn --timeout 0 --reload app:app
```

## [2] 파인 튜닝

### 2.1. supervised
```sh
uv run fine_tuning/supervised/data_gen.py
```
- `fine_tuning/supervised/data.jsonl`파일 생성