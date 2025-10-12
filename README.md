# OpenAI Agent School - Fine Tuning

- 환경변수 `.env`파일에 `OPENAI_API_KEY`를 등록해야 정상적으로 업로드 가능

## [1] SFT (Supervised Fine-tuning)

- 프로젝트 위치: `sft/`
- 입력 데이터 위치 (yaml): `sft/data`
- 출력 데이터 위치 (jsonl): `sft/output`
- 데이터 생성 및 업로드 
    ```sh
    uv run sft/convert_and_upload.py
    ```

## [2] DPO (Direct Preference Optimization)

- 프로젝트 위치: `dpo/`
- 입력 데이터 위치 (yaml): `dpo/data`
- 출력 데이터 위치 (jsonl): `dpo/output`
- 데이터 생성 및 업로드 
    ```sh
    uv run dpo/convert_and_upload.py
    ```

## [3] RFT (Reinforcement Fine-tuning)

- 프로젝트 위치: `rft/`
- 입력 데이터 위치 (yaml): `rft/data`
- 출력 데이터 위치 (json, jsonl): `rft/output`
- 데이터 생성 및 업로드 
    ```sh
    uv run rft/convert_and_upload.py
    ```