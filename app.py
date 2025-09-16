from flask import Flask, request, Response, render_template, redirect, url_for, make_response
from flask_cors import CORS
import os, json, hashlib
from openai import OpenAI
import json5

# environment variables
from dotenv import load_dotenv
load_dotenv()

def deep_merge(base_dict, override_dict):
    if not isinstance(override_dict, dict):
        return override_dict
    
    result = base_dict.copy()
    
    for key, value in override_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
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

# OpenAI 클라이언트
client = OpenAI()

# config
config = {}
if os.environ.get("PROMPT_ID"):
    config = {"prompt": { "id": os.environ["PROMPT_ID"] }}
    print(f"Using prompt ID from environment: {os.environ['PROMPT_ID']}")
else:
    config = {"model": "gpt-5"}
    print("Using default model: gpt-5")

# config.overrides.jsonc
config_overrides = load_config_overrides()
if config_overrides:
    config = deep_merge(config, config_overrides)
    print(f"Applied config overrides. Final config: {json.dumps(config, indent=2)}")

# Flask 앱 초기화
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# 모든 도메인 허용
CORS(app) 

# 토큰 생성 함수
def generate_auth_token():
    password = os.environ.get('PASSWORD', '').strip()
    return hashlib.md5(f"{password}salt".encode()).hexdigest()

# 패스워드 체크 함수
def check_password_required():
    password = os.environ.get('PASSWORD', '').strip()
    return bool(password)

def is_authenticated():
    if not check_password_required():
        return True
    auth_token = request.cookies.get('auth_token')
    return auth_token == generate_auth_token()

@app.route("/login", methods=["GET", "POST"])
def login():
    if not check_password_required():
        return redirect(url_for('index'))
    
    if request.method == "POST":
        password = request.form.get('password', '').strip()
        env_password = os.environ.get('PASSWORD', '').strip()
        if password == env_password:
            response = make_response(redirect(url_for('index')))
            response.set_cookie('auth_token', generate_auth_token(), max_age=60*60*24*30)  # 30일
            return response
        else:
            return render_template('login.html', error="Invalid password.")
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('auth_token', '', expires=0)
    return response

@app.route("/")
def index():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    if title := os.environ.get("TITLE"):
        title = title.strip()
    else:
        title = "🤖 OpenAI API Agent School"
    return render_template('index.html', 
                         title=title,
                         config={'PASSWORD': os.environ.get('PASSWORD')})

@app.route("/api/chat", methods=["POST"])
def chat_api():
    if not is_authenticated():
        return Response(json.dumps({'type': 'error', 'message': 'Unauthorized'}), 
                       status=401, mimetype='application/json')
        
    data = request.get_json()
    input_message = data.get("input_message", [])
    previous_response_id = data.get("previous_response_id")

    def generate():
        nonlocal previous_response_id
        try:
            # 첫 번째 API 호출 - config 복사 후 명시적 파라미터로 업데이트
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
                    # config 복사 후 명시적 파라미터로 업데이트
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

    return Response(generate(), mimetype='text/plain')

if __name__ == "__main__":
    app.run()