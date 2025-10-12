import os, yaml
from openai import OpenAI
from dotenv import load_dotenv

def get_config():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

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

def get_prompt_id():
    load_dotenv(override=True)
    return os.environ.get("PROMPT_ID")

def get_title():
    load_dotenv(override=True)
    return os.environ.get("TITLE", "OpenAI Agent School").strip()
