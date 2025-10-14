# OpenAI Agent School

[(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI Agent School** ](https://openai-agent.aicastle.school/)(OpenAI를 활용한 나만의 AI 에이전트 만들기) 강의 자료입니다.

## [1] Chat Server
### 준비 사항
- 환경변수 (.env)
    - `OPENAI_API_KEY` : OpenAI API Key
    - `PROMPT_ID` : Chat 프롬프트 ID
    - `TITLE` : 앱에서 사용할 제목
- [functions.py](functions.py)
    - Function Call에서 사용할 함수를 정의
- [prompt_variables.yaml](prompt_variables.yaml)
    - prompt variables를 정의

### 서버 실행
```bash
uv run chat.py
```
- 실행 포트: `8000`
- 접속 URL: <http://localhost:8000>
- 쿼리 파라미터로 prompt variable을 전달 가능
    - (예) `http://localhost:8000?user_name=홍길동&user_age=19`

## [2] MCP Server

### 준비 사항
- [functions.py](functions.py)
    - MCP 툴에 등록될 함수를 정의

### 서버 실행
```
uv run mcp.py
```
- 실행 포트: `8001`



## [3] Fine Tuning

### 준비사항
- 환경변수 (.env)
    - `OPENAI_API_KEY` : OpenAI API Key


### 3.1. SFT (Supervised Fine-tuning)

- 프로젝트 위치: `fine-tuning/sft/`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine-tuning/sft/convert_and_upload.py
    ```

### 3.2. DPO (Direct Preference Optimization)

- 프로젝트 위치: `fine-tuning/dpo/`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine-tuning/dpo/convert_and_upload.py
    ```

### 3.3. RFT (Reinforcement Fine-tuning)

- 프로젝트 위치: `fine-tuning/rft/`
- 입력 데이터 위치 (yaml): `rft/data`
- 출력 데이터 위치 (json, jsonl): `rft/output`
- 데이터 생성 및 업로드 
    ```sh
    uv run fine-tuning/rft/convert_and_upload.py
    ```

## 부록

### KEEPALIVE_URL
- 주기적으로 ping 작업을 수행
- 레포지토리 > settings > Secrets and Variables > Actions > New repository secret
    - Name: `KEEPALIVE_URL`
    - Secret: `https://<your-url>`
- Actions 탭에서 Actions 및 아래 파일을 활성화
    - `.github/workflows/keepalive-url.yml`
    - `.github/workflows/keepalive-workflow-enabled.yml`