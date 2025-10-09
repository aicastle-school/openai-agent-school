from dotenv import load_dotenv
import os, json
from openai import OpenAI

# openai client 생성 함수
def get_openai_client():
    global client, OPENAI_API_KEY
    client = client if 'client' in globals() else None
    OPENAI_API_KEY = OPENAI_API_KEY if 'OPENAI_API_KEY' in globals() else None

    load_dotenv(override=True)
    current_api_key = os.environ.get("OPENAI_API_KEY")
    if OPENAI_API_KEY != current_api_key:
        OPENAI_API_KEY = current_api_key
        client = OpenAI() if OPENAI_API_KEY else None
    return client

# API 파라미터 생성 함수
def get_api_params():
    load_dotenv(override=True)

    if PROMPT_ID := os.environ.get("PROMPT_ID"):
        api_params = {"prompt": {"id": PROMPT_ID}}
    else:
        api_params = {"model": "gpt-5"}
    
    for target_folder in ['./', '/etc/secrets/']:
        # tools.json
        if path := os.path.join(target_folder, "tools.json"):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    api_tools = json.load(file)
                    api_params["tools"] = api_tools
                break
            except Exception as e:
                continue
        
        # variables.json
        if path := os.path.join(target_folder, "variables.json"):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    api_variables = json.load(file)
                    if PROMPT_ID:
                        api_params['prompt']["variables"] = api_variables
                break
            except Exception as e:
                continue

    return api_params

# TITLE 가져오는 함수
def get_title():
    load_dotenv(override=True)
    return os.environ.get("TITLE", "OpenAI Agent School").strip()
