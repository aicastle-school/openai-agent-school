from fastapi import FastAPI, Request, HTTPException, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os, json, hashlib, inspect
from openai import OpenAI
import json5
from fastmcp import FastMCP
from typing import Optional
import uvicorn

# 환경변수
from dotenv import load_dotenv
load_dotenv()

##################################################################
########################## FastAPI Setup #########################
##################################################################

# MCP 서버 설정 (lifespan 사용을 위해 먼저 생성)
mcp = FastMCP("MCP Server")

# tools.py 모듈의 모든 함수를 MCP 툴로 등록
import tools
for name, fn in inspect.getmembers(tools, inspect.isfunction):
    mcp.tool(fn)

# MCP 앱 생성
mcp_app = mcp.http_app()

# FastAPI 앱 생성 (MCP lifespan 연결)
app = FastAPI(lifespan=mcp_app.lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#################################################################
######################## MCP Server #############################
#################################################################

# MCP POST 요청 처리 (실제 MCP 통신)
@app.api_route("/mcp", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def mcp_handler(request: Request):
    return await mcp_app(request.scope, request.receive, request._send)


# MCP 비밀번호 보호 미들웨어
if PASSWORD := os.getenv("PASSWORD", ""):
    @app.middleware("http")
    async def mcp_auth_middleware(request: Request, call_next):
        if request.url.path == "/mcp" :
            password_param = request.query_params.get("password")
            if not password_param or password_param != PASSWORD:
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)

##################################################################
######################## Agent App ###############################
##################################################################

# OpenAI 클라이언트
client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

# 템플릿 설정
templates = Jinja2Templates(directory="templates")


def apply_config_overrides(base_dict, override_dict):
    if not isinstance(override_dict, dict):
        return override_dict
    
    result = base_dict.copy()
    
    for key, value in override_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = apply_config_overrides(result[key], value)
        else:
            result[key] = value
    
    return result

def load_config_overrides():
    override_paths = [
        './config.overrides.jsonc',
        '/etc/secrets/config.overrides.jsonc',
    ]
    
    for path in override_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    content = f.read()
                overrides = json5.loads(content)
                print(f"Loaded config overrides from: {path}")
                return overrides
            except Exception as e:
                print(f"Error loading config overrides from {path}: {e}")
                continue
    
    print("No config overrides found")
    return {}

# config 설정
config = {}
if os.environ.get("PROMPT_ID"):
    config = {"prompt": { "id": os.environ["PROMPT_ID"] }}
    print(f"Using prompt ID from environment: {os.environ['PROMPT_ID']}")
else:
    config = {"model": "gpt-5"}
    print("Using default model: gpt-5")

# config.overrides.jsonc 적용
config_overrides = load_config_overrides()
if config_overrides:
    config = apply_config_overrides(config, config_overrides)
    print(f"Applied config overrides. Final config: {json.dumps(config, indent=2)}")

# 인증 관련 함수들
def generate_auth_token():
    password = os.environ.get('PASSWORD', '').strip()
    return hashlib.md5(f"{password}salt".encode()).hexdigest()

def check_password_required():
    password = os.environ.get('PASSWORD', '').strip()
    return bool(password)

def is_authenticated(auth_token: Optional[str] = None):
    if not check_password_required():
        return True
    return auth_token == generate_auth_token()


# 로그인 페이지
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    if not check_password_required():
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login_submit(password: str = Form(...)):
    if not check_password_required():
        return RedirectResponse(url="/", status_code=302)
    
    env_password = os.environ.get('PASSWORD', '').strip()
    if password.strip() == env_password:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("auth_token", generate_auth_token(), max_age=60*60*24*30)
        return response
    else:
        return RedirectResponse(url="/login?error=Invalid password", status_code=302)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("auth_token")
    return response

# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, auth_token: Optional[str] = Cookie(None)):
    if not is_authenticated(auth_token):
        return RedirectResponse(url="/login", status_code=302)
    
    title = os.environ.get("TITLE", "🤖 OpenAI API Agent School").strip()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": title,
        "config": {'PASSWORD': os.environ.get('PASSWORD')}
    })

### 채팅 API 
@app.post("/api/chat")
async def chat_api(request: Request, auth_token: Optional[str] = Cookie(None)):
    if not is_authenticated(auth_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # OpenAI 클라이언트 검증
    if client is None:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
    
    data = await request.json()
    input_message = data.get("input_message", [])
    previous_response_id = data.get("previous_response_id")

    async def generate():
        nonlocal previous_response_id
        try:
            # 첫 번째 API 호출
            api_params = config.copy()
            api_params.update({
                'input': input_message,
                'previous_response_id': previous_response_id,
                'stream': True
            })
            response = client.responses.create(**api_params)

            max_repeats = 5
            for _ in range(max_repeats):
                follow_up_input = []
                for event in response:
                    print(f"Processing event type: {event.type}")
                    
                    # 이벤트 타입을 클라이언트에 전송
                    yield f"data: {json.dumps({'type': 'status', 'status': event.type})}\n\n"
                    
                    if event.type == "response.output_text.delta":
                        yield f"data: {json.dumps({'type': 'text_delta', 'delta': event.delta})}\n\n"

                    elif event.type == "response.completed":
                        previous_response_id = event.response.id

                    elif event.type == "response.image_generation_call.partial_image":
                        image_data_url = f"data:image/{event.output_format};base64,{event.partial_image_b64}"
                        yield f"data: {json.dumps({'type': 'image_generated', 'image_data': image_data_url, 'is_partial': True})}\n\n"

                    elif event.type == "response.output_item.done":
                        if event.item.type == "function_call":
                            try:
                                import tools
                                func = getattr(tools, event.item.name)
                                args = json.loads(event.item.arguments)
                                func_output = str(func(**args))
                            except Exception as e:
                                func_output = str(e)
                            finally:
                                follow_up_input.append({
                                    "type": "function_call_output", 
                                    "call_id": event.item.call_id, 
                                    "output": func_output
                                })
                        elif event.item.type == "mcp_approval_request":
                                follow_up_input.append({
                                    "type": "mcp_approval_response",
                                    "approval_request_id": event.item.id,
                                    "approve": True
                                })
                            
                # 함수 호출 결과가 있으면 다시 API 호출
                if follow_up_input:
                    print(f"Making follow-up API call with {len(follow_up_input)}")
                    api_params = config.copy()
                    api_params.update({
                        'input': follow_up_input,
                        'previous_response_id': previous_response_id,
                        'stream': True
                    })
                    response = client.responses.create(**api_params)
                else:
                    break

            yield f"data: {json.dumps({'type': 'done', 'response_id': previous_response_id})}\n\n"
            print("Stream completed successfully")

        except Exception as e:
            print(f"Error in chat API: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/plain")



##################################################################
####################### Server Startup ##########################
##################################################################

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting unified server on port {port}")
    print(f"🤖 Agent App: http://localhost:{port}")
    print(f"🔧 MCP Server: http://localhost:{port}/mcp")
    
    uvicorn.run(
        f"main:app",  # 동적으로 모듈명 생성
        host="0.0.0.0",
        port=port,
        reload=True,
        timeout_keep_alive=0,  # timeout 무제한
        timeout_graceful_shutdown=0,
        access_log=True,
        log_level="info"
    )