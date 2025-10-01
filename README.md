# OpenAI API Agent School - Project

[![smithery badge](https://smithery.ai/badge/@aicastle-school/openai-api-agent-project)](https://smithery.ai/server/@aicastle-school/openai-api-agent-project)

본 자료는 [(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI API로 배우는 Agent 개발 첫걸음** ](https://openai-api-agent.aicastle.school/)(OpenAI API Agent School) 강의 프로젝트 자료입니다.


### Installing via Smithery

To install openai-api-agent-project automatically via [Smithery](https://smithery.ai/server/@aicastle-school/openai-api-agent-project):

```bash
npx -y @smithery/cli install @aicastle-school/openai-api-agent-project
```

## [0] Install & Build (uv)

```sh
# uv Install
curl -LsSf https://astral.sh/uv/install.sh | sh

# uv Build
uv sync --frozen && uv cache prune --ci
```


## [1] 프로젝트 세팅

### 1.1. 환경 변수 (.env)

- **.env 파일**로 설정하거나 **배포 환경에서 지정**
- `OPENAI_API_KEY`: Agent 앱 또는 파인튜닝할 데이터를 업로드할 때 사용할 OpenAI API 키
- `PROMPT_ID`: Agent 앱에서 사용할 OpenAI 프롬프트 ID 
- `TITLE`: Agent앱의 상단 제목

### 1.2. api_params.overrides.jsonc

### 1.2. api_params.jsonc

- Agent 앱에서 OpenAI API 요청시 responses.create()에서 사용할 파라미터 설정
- **api_params.jsonc 파일**로 설정하거나 **배포 환경에서 지정**
- 파일 위치
    - ./api_params.jsonc
    - /etc/secrets/api_params.jsonc


### 1.3. tools.py

- Agent 앱에서 Function Calling으로 사용할 함수.
- 또는 MCP 서버에서 tool로 사용할 함수.
- 파일 위치: [tools.py](tools.py)

## [2] 앱 실행

### 실행

```sh
uv run main.py
```

- 포트: 환경변수 `PORT`값이 지정된 경우 이 값을 사용하며, 그렇지 않을 경우 `8000`을 사용함.

- Agent 앱 주소: <https://localhost:8000/>

- MCP 서버 주소: <https://localhost:8000/mcp>

### KEEPALIVE_URL
- 실행 중인 앱이 일정시간 동안 접속이 없으면 유휴상태가 될 경우 `KEEPALIVE_URL`를 github actions의 환경변수(secrets)에 지정하여 주기적으로 접속하는 cron 작업을 수행할 수 있음.
- Fork한 경우 Fork한 레포지토리 접속하여 상단의 Actions 탭에서 Actions 및 .github/workflows/keepalive-url.yml 을 활성화 하세요.
- 레포지토리 > settings > Secrets and Variables > Actions > New repository secret 에 접속하여 아래와 같이 입력 (Secret에는 본인이 배포한 URL로 입력)
- 예시
    - Name: `KEEPALIVE_URL`
    - Secret: `https://<your-project-name>.onrender.com`


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

