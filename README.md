# OpenAI Agent School

본 자료는 [(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI를 활용한 Agent 개발 첫걸음** ](https://openai-agent.aicastle.school/)(OpenAI Agent School) 강의 프로젝트 자료입니다.

## MCP

### 실행

```sh
uv run main.py
```

- 포트: 환경변수 `PORT`값이 지정된 경우 이 값을 사용하며, 그렇지 않을 경우 `8001`을 사용함.

- URL: <https://localhost:8001/mcp>


## Fine Tuning

- 환경변수 `.env`파일에 `OPENAI_API_KEY`를 등록해야 정상적으로 업로드 가능합니다.

### SFT (Supervised Fine-tuning)

- 프로젝트 위치: `sft/`
- 입력 데이터 위치 (yaml): `sft/data`
- 출력 데이터 위치 (jsonl): `sft/output`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine-tuning/sft/convert_and_upload.py
    ```

### DPO (Direct Preference Optimization)

- 프로젝트 위치: `dpo/`
- 입력 데이터 위치 (yaml): `dpo/data`
- 출력 데이터 위치 (jsonl): `dpo/output`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine-tuning/dpo/convert_and_upload.py
    ```

### RFT (Reinforcement Fine-tuning)

- 프로젝트 위치: `rft/`
- 입력 데이터 위치 (yaml): `rft/data`
- 출력 데이터 위치 (json, jsonl): `rft/output`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine-tuning/rft/convert_and_upload.py
    ```

## KEEPALIVE_URL
- [render](https://render.com)와 같은 클라우드 플랫폼에 배포시 일정시간 동안 접속이 없으면 유휴상태가 되는 것을 방지합니다.
- `KEEPALIVE_URL`을 github actions의 환경변수(secrets)에 지정하여 주기적으로 ping 작업을 수행할 수 있습니다.
- Fork한 경우 Fork한 레포지토리 접속하여 상단의 Actions 탭에서 Actions 및 아래 파일을 활성화 하세요
    - `.github/workflows/keepalive-url.yml`
    - `.github/workflows/keepalive-workflow-enabled.yml`
- 레포지토리 > settings > Secrets and Variables > Actions > New repository secret 에 접속하여 아래와 같이 입력 하세요.
- 예시
    - Name: `KEEPALIVE_URL`
    - Secret: `https://<your-project-name>.onrender.com`