#!/usr/bin/env python3
import os, yaml, json, glob

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')
output_file = os.path.join(script_dir, 'data.jsonl')

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
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

response = client.files.create(
    file=open(output_file, "rb"),
    purpose="fine-tune",
)
print("[INFO] 파일 업로드 완료: ", response.id)

################ convert grader.yaml to grader.json ###############

grader_yaml_file = os.path.join(script_dir, 'grader.yaml')
grader_json_file = os.path.join(script_dir, 'grader.json')

with open(grader_yaml_file, 'r', encoding='utf-8') as f:
    grader_data = yaml.safe_load(f)

with open(grader_json_file, 'w', encoding='utf-8') as f:
    json.dump(grader_data, f, ensure_ascii=False, indent=2)

print(f"[INFO] grader 변환 완료: {grader_json_file}")