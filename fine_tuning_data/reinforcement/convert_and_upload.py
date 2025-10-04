#!/usr/bin/env python3
import os, yaml, json, glob
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')
output_dir = os.path.join(script_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

# 현재 날짜를 YYYY-MM-DD 형식으로 생성
current_date = datetime.now().strftime('%Y-%m-%d')
output_file = os.path.join(output_dir, f'data-reinforcement-{current_date}.jsonl')

################ convert yaml to jsonl ###############

# YAML 파일 패턴들
data_patterns = [
    os.path.join(data_dir, '*.yaml'),
    os.path.join(data_dir, '*.yml')
]

yaml_files = []
for pattern in data_patterns:
    yaml_files.extend(glob.glob(pattern))

with open(output_file, 'w', encoding='utf-8') as jsonl_file:
    for yaml_file in sorted(yaml_files):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            if data := yaml.safe_load(f):
                jsonl_file.write(json.dumps(data, ensure_ascii=False) + '\n')

print(f"[INFO] 파일 생성 완료: {output_file}")

############## upload data ###############
upload_confirm = input(f"OpenAI에 파일을 업로드하시겠습니까? ({output_file}) [y/N]: ")

if upload_confirm.lower() in ['y', 'yes']:
    from dotenv import load_dotenv
    load_dotenv()

    from openai import OpenAI
    client = OpenAI()

    response = client.files.create(
        file=open(output_file, "rb"),
        purpose="fine-tune",
    )
    print("[INFO] 파일 업로드 완료: ", response.id)
else:
    print("[INFO] 파일 업로드를 건너뛰었습니다.")

################ convert grader.yaml to grader.json ###############

grader_yaml_file = os.path.join(script_dir, 'grader.yaml')
grader_json_file = os.path.join(output_dir, f'grader-reinforcement-{current_date}.json')

with open(grader_yaml_file, 'r', encoding='utf-8') as f:
    grader_data = yaml.safe_load(f)

with open(grader_json_file, 'w', encoding='utf-8') as f:
    json.dump(grader_data, f, ensure_ascii=False, indent=2)

print(f"[INFO] grader 변환 완료: {grader_json_file}")