from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os, json
from openai import OpenAI
import uvicorn
import httpx
from dotenv import load_dotenv
from mcp_server import mcp
from api_params import get_api_params

# 환경변수 로드
load_dotenv()

# app 생성
mcp_app = mcp.http_app(path="/")
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)
# app = FastAPI()

# app 설정
app.add_middleware(CORSMiddleware, allow_origins=["*"]) # CORS - 모든 출처 허용
app.mount("/static", StaticFiles(directory="assets/static"), name="static") # Static 파일 서빙 설정
templates = Jinja2Templates(directory="assets/templates") # 템플릿 설정

# OpenAI 클라이언트 생성
client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

# API 파라미터 설정
api_params = get_api_params()


# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    title = os.environ.get("TITLE", "🤖 OpenAI API Agent School").strip()
    return templates.TemplateResponse(request, "index.html", {
        "title": title
    })

# 채팅 API
@app.post("/api")
async def chat_api(request: Request):
    if client is None:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
    
    data = await request.json()
    input_message = data.get("input_message", [])
    previous_response_id = data.get("previous_response_id")

    async def generate():
        nonlocal previous_response_id
        try:
            request_params = api_params.copy()
            request_params.update({
                'input': input_message,
                'previous_response_id': previous_response_id,
                'stream': True
            })
            response = client.responses.create(**request_params)

            max_repeats = 5
            for _ in range(max_repeats):
                follow_up_input = []
                annotations = []
                try:
                    for event in response:
                        print(f"Processing event type: {event.type}")
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
                            elif event.item.type == "message":
                                for content in event.item.content:
                                    content_dict = content.model_dump()
                                    if 'annotations' in content_dict:
                                        annotations += content_dict['annotations']
                except Exception as stream_error:
                    print(f"Error in stream processing: {stream_error}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Stream error: {str(stream_error)}'})}\n\n"
                    break  # 스트림 에러가 발생하면 루프 중단

                            
                # 함수 호출 결과가 있으면 다시 API 호출
                if follow_up_input:
                    print(f"Making follow-up API call with {len(follow_up_input)}")
                    request_params = api_params.copy()
                    request_params.update({
                        'input': follow_up_input,
                        'previous_response_id': previous_response_id,
                        'stream': True
                    })
                    response = client.responses.create(**request_params)
                else:
                    break

            yield f"data: {json.dumps({'type': 'done', 'response_id': previous_response_id, 'annotations': annotations})}\n\n"
            print("Stream completed successfully")

        except Exception as e:
            print(f"Error in chat API: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/plain")

# 파일 프록시 엔드포인트 - sandbox 파일을 다운로드할 수 있게 해줌
@app.get("/files/{container_id}/{file_id}")
async def proxy_sandbox_file(container_id: str, file_id: str, filename: str = None):
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured")
    
    try:
        # OpenAI Container Files API 호출
        url = f"https://api.openai.com/v1/containers/{container_id}/files/{file_id}/content"
        headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
        
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(url, headers=headers)
            response.raise_for_status()
            
            # 파일명 결정: 파라미터로 받은 filename이 있으면 사용, 없으면 file_id 사용
            download_filename = filename if filename else file_id
            
            # 파일 내용과 헤더를 클라이언트에게 전달
            content_type = response.headers.get("content-type", "application/octet-stream")
            return Response(
                content=response.content, 
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename={download_filename}",
                    "Cache-Control": "public, max-age=3600"
                }
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error proxying file: {str(e)}")

##################################################################
####################### Server Startup ##########################
##################################################################

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting unified server on port {port}")
    print(f"🤖 Agent App: http://localhost:{port}/")
    print(f"🔧 MCP Server: http://localhost:{port}/mcp")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        timeout_keep_alive=0,  # timeout 무제한
        timeout_graceful_shutdown=0,
        access_log=True,
        log_level="info"
    )