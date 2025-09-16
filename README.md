# OpenAI API Agent School - Project

본 자료는 [(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI API로 배우는 Agent 개발 첫걸음** ](https://openai-api-agent.aicastle.school/)(OpenAI API Agent School) 강의 프로젝트 자료입니다.


## [0] Install & Build (uv)

```sh
# uv Install
curl -LsSf https://astral.sh/uv/install.sh | sh

# uv Build
uv sync --frozen && uv cache prune --ci
```


## [1] Agent 앱

### 1.1. 프로젝트 세팅

#### 환경 변수 (필수)

- 환경변수를 프로젝트 폴더의 .env 파일로 설정하거나 배포 환경에서 등록
- 코드스페이스 실행 시 예제 파일 ([.devcontainer/example/.env](.devcontainer/example/.env))이 자동으로 프로젝트 폴더로 복사됨.

    > `OPENAI_API_KEY`: OpenAI API키를 설정  
    > `PROMPT_ID` (옵션): OpenAI 대시보드에서 프롬프트 ID 입력  
    > `TITLE` (옵션): 실행 될 앱의 상단 제목  
    > `PASSWORD` (옵션): 비밀번호가 설정된 앱을 원할경우 입력

#### config.overrides.jsonc (선택)

- openai responses api 요청시 덮어쓸 파라미터가 있다면 config.overrides.jsonc에 정의.
- 파일 위치: 프로젝트 폴더 (우선) 또는 /etc/secrets/
- 코드스페이스 실행 시 예제 파일 ([.devcontainer/example/config.overrides.jsonc](.devcontainer/example/config.overrides.jsonc))이 자동으로 프로젝트 폴더로 복사됨

#### function_call.py (선택)

- function_call에서 사용할 함수를 [function_call.py](function_call.py)에 작성.

### 1.2. 앱 실행

```sh
uv run gunicorn --timeout 0 --reload app:app
```
- 기본 포트: `8000`

## [2] MCP 서버

### 2.1. mcp_server.py 작성
- [mcp_server.py](mcp_server.py)에 mcp 툴을 정의합니다.

### 2.2. 서버 실행
```sh
uv run mcp_server.py
```
- 기본 포트: `8081`


## [3] 파인 튜닝 데이터

`.env`파일에 `OPENAI_API_KEY`를 등록해야 정상적으로 업로드 가능

### 3.1. SFT (Supervised Fine-tuning)

- 폴더 위치: `fine_tuning_data/supervised/`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine_tuning_data/supervised/convert_and_upload.py
    ```

### 3.2. DPO (Direct Preference Optimization)

- 폴더 위치: `fine_tuning_data/preference/`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine_tuning_data/preference/convert_and_upload.py
    ```

### 3.3. RFT (Reinforcement Fine-tuning)

- 폴더 위치: `fine_tuning_data/reinforcement/`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine_tuning_data/reinforcement/convert_and_upload.py
    ```