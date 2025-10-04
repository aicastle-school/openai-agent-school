#!/usr/bin/env python3
import os, yaml, json, glob
from datetime import datetime
import pytz

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')
output_dir = os.path.join(script_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

# 현재 날짜를 YYMMDD-HHMMSS 형식으로 생성 (한국시간)
kst = pytz.timezone('Asia/Seoul')
current_date = datetime.now(kst).strftime('%y%m%d-%H%M%S')
output_file = os.path.join(output_dir, f'data-dpo-{current_date}.jsonl')

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
