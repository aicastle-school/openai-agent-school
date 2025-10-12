# OpenAI Agent School

본 자료는 [(주)에이아이캐슬](https://aicastle.com)에서 만든 [**OpenAI를 활용한 Agent 개발 첫걸음** ](https://openai-agent.aicastle.school/)(OpenAI Agent School) 강의 프로젝트 자료입니다.


## 프로젝트 시작하기

각 프로젝트는 branch 별로 사용 가능합니다.

### [Multi Agent](https://github.com/aicastle-school/openai-agent-school/tree/multi-agent)
- 다중 에이전트 앱 프로젝트
- branch: [`multi-agent`](https://github.com/aicastle-school/openai-agent-school/tree/multi-agent)


### [Single Agent](https://github.com/aicastle-school/openai-agent-school/tree/single-agent)
- 싱글 에이전트 앱 프로젝트
- branch: [`single-agent`](https://github.com/aicastle-school/openai-agent-school/tree/single-agent)

### [Fine Tuning](https://github.com/aicastle-school/openai-agent-school/tree/fine-tuning)
- Fine Tuning (미세조정) 프로젝트
- branch: [`fine-tuning`](https://github.com/aicastle-school/openai-agent-school/tree/fine-tuning)

### [MCP](https://github.com/aicastle-school/openai-agent-school/tree/mcp)
- MCP 프로젝트
- branch: [`mcp`](https://github.com/aicastle-school/openai-agent-school/tree/mcp)

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