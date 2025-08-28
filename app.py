from flask import Flask, request, Response, render_template, send_file
import os, yaml, base64, json, tempfile, threading
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트
client = OpenAI()

# config
config = {}
if os.environ["PROMPT_ID"]:
    config["prompt"] = {
        "id": os.environ["PROMPT_ID"],
        "variables": yaml.safe_load(open("prompt_variables.yaml"))
    }
try:
    from prompt_tools import tools
    if tools:
        config["tools"] = tools
except:
    pass

# Flask 앱 초기화
app = Flask(__name__)

# 임시 파일 저장 디렉토리
TEMP_DIR = Path(tempfile.gettempdir()) / "images"
TEMP_DIR.mkdir(exist_ok=True)

@app.route("/")
def index():
    app_title = os.environ.get("APP_TITLE")
    if not app_title:
        app_title = "OpenAI API Agent School"
    return render_template('index.html', app_title=app_title)

@app.route("/api/chat", methods=["POST"])
def chat_api():    
    data = request.get_json()
    input_message = data.get("input_message", [])
    previous_response_id = data.get("previous_response_id")

    def generate():
        nonlocal previous_response_id
        try:
            response = client.responses.create(
                input=input_message,
                previous_response_id=previous_response_id,
                stream=True,
                **config
            )

            max_repeats = 5
            for _ in range(max_repeats):
                follow_up_input = []
                for event in response:
                    print(f"Processing event type: {event.type}")
                    if event.type == "response.output_text.delta":
                        yield f"data: {json.dumps({'type': 'text_delta', 'delta': event.delta})}\n\n"

                    elif event.type == "response.completed":
                        previous_response_id = event.response.id

                    elif event.type == "response.image_generation_call.partial_image":
                        image_name = f"{event.item_id}.{event.output_format}"
                        file_path = TEMP_DIR / image_name
                        with open(file_path, 'wb') as f:
                            f.write(base64.b64decode(event.partial_image_b64))
                        threading.Timer(60.0, lambda: file_path.unlink(missing_ok=True)).start()
                        yield f"data: {json.dumps({'type': 'image_generated', 'image_url': f"/image/{image_name}", 'is_partial': True})}\n\n"

                    elif event.type == "response.output_item.done":
                        if event.item.type == "function_call":
                            try:
                                import function_call
                                func = getattr(function_call, event.item.name)
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
                    response = client.responses.create(
                        input=follow_up_input,
                        previous_response_id=previous_response_id,
                        stream=True,
                        **config
                    )
                else:
                    break

            yield f"data: {json.dumps({'type': 'done', 'response_id': previous_response_id})}\n\n"
            print("Stream completed successfully")

        except Exception as e:
            print(f"Error in chat API: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/plain')

@app.route('/image/<image_name>')
def serve_image(image_name):
    return send_file(
        TEMP_DIR / image_name,
        mimetype=f'image/{image_name.split(".")[-1]}',
        as_attachment=False
    )

if __name__ == "__main__":
    app.run()