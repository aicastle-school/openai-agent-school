# OpenAI Agent School - Single Agent

## [1] Render에 배포

[**Render**](https://render.com/) 접속 후 새 Web Service 생성 후 Github Repository 선택

#### Config 설정

- Language: `Python 3`
- Branch: `render-chat`
- Region: `Singapore`
- Build Command: 
    ```sh
    uv sync
    ```
- Start Command
    ```sh
    uv run main.py
    ```
- Instance Type: Free (안정적인 사용을 원하면 유료 플랜 권장)
- Environment Variables
    - `OPENAI_API_KEY`: OpenAI API Key
    - `PROMPT_ID`: Prompt ID (Chat에서 생성된 Prompt ID)

### KEEPALIVE_URL
- 주기적으로 ping 작업을 수행
- 레포지토리 > settings > Secrets and Variables > Actions > New repository secret
    - Name: `KEEPALIVE_URL`
    - Secret: `https://<your-url>`
- Actions 탭에서 Actions 및 아래 파일을 활성화
    - `.github/workflows/keepalive-url.yml`
    - `.github/workflows/keepalive-workflow-enabled.yml`


## [2] 코드스페이스에서 실행
- 환경변수 (.env)
    - `OPENAI_API_KEY`: OpenAI API Key
    - `PROMPT_ID`: Prompt ID (Chat에서 생성된 Prompt ID)

- 실행 명령어
    ```sh
    uv run main.py
    ```
- 포트: 환경변수 `PORT`값이 지정된 경우 이 값을 사용하며, 그렇지 않을 경우 `8000`을 사용함.
- URL
    - APP: <https://localhost:8000>
    - MCP: <https://localhost:8000/mcp>