# OpenAI Agent School - Single Agent

## [1] Render에 배포

- [**Render**](https://render.com/) 접속 후 새 Web Service 생성
- Github Repository 선택
    - (옵션1) 내 레포지토리 선택: Git Provider > Connect
    - (옵션2) 공개 레포지토리 선택: `https://github.com/aicastle-school/openai-api-agent-project`

#### Config 설정

- Language: `Python 3`
- Branch: `single-agent`
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
- Secret Files (선택 사항)
    - `config.yaml`
    - `functions.py`: function call 및 mcp에서 사용할 함수

## [2] 코드스페이스에서 실행

```sh
uv run main.py
```

## References
- OpenAI Docs
    - [chatkit](https://platform.openai.com/docs/guides/chatkit)
    - [chatkit-themes](https://platform.openai.com/docs/guides/chatkit-themes)
- ChatKit JS
    - [github](https://github.com/openai/chatkit-js)
    - [docs](https://openai.github.io/chatkit-js/)