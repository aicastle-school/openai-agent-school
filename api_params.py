import os
import json
import json5

def apply_api_overrides(base_dict, override_dict):
    """API 파라미터에 override를 적용하는 함수"""
    if not isinstance(override_dict, dict):
        return override_dict
    
    result = base_dict.copy()
    
    for key, value in override_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = apply_api_overrides(result[key], value)
        else:
            result[key] = value
    
    return result

def load_api_overrides():
    """api_params.jsonc 파일을 로드하는 함수"""
    override_paths = [
        './api_params.jsonc',
        '/etc/secrets/api_params.jsonc',
    ]
    
    for path in override_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    content = f.read()
                overrides = json5.loads(content)
                print(f"Loaded API parameter overrides from: {path}")
                return overrides
            except Exception as e:
                print(f"Error loading API parameter overrides from {path}: {e}")
                continue
    
    print("No API parameter overrides found")
    return {}

def get_api_params():
    """최종 API 파라미터를 반환하는 함수"""
    # 기본 API 파라미터 설정
    if os.environ.get("PROMPT_ID"):
        api_params = {"prompt": {"id": os.environ["PROMPT_ID"]}}
        print(f"Using prompt ID from environment: {os.environ['PROMPT_ID']}")
    else:
        api_params = {"model": "gpt-5"}
        print("Using default model: gpt-5")

    # API 파라미터 overrides 적용
    param_overrides = load_api_overrides()
    if param_overrides:
        api_params = apply_api_overrides(api_params, param_overrides)
        print(f"Applied API parameter overrides. Final API params: {json.dumps(api_params, indent=2)}")
    
    return api_params