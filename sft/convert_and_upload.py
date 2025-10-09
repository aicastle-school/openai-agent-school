#!/usr/bin/env python3
import os, yaml, json, glob
from datetime import datetime
import pytz
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
    
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

# 현재 날짜를 YYMMDD-HHMMSS 형식으로 생성 (한국시간)
kst = pytz.timezone('Asia/Seoul')
current_date = datetime.now(kst).strftime('%y%m%d-%H%M%S')

################ train_data ###############
train_file = os.path.join(output_dir, f'{current_date}-sft-train.jsonl')
train_data_dir = os.path.join(script_dir, 'data/train')
try:
    # YAML 파일 패턴들
    train_data_patterns = [
        os.path.join(train_data_dir, '*.yaml'),
        os.path.join(train_data_dir, '*.yml')
    ]

    yaml_files = []
    for pattern in train_data_patterns:
        yaml_files.extend(glob.glob(pattern))

    with open(train_file, 'w', encoding='utf-8') as jsonl_file:
        for yaml_file in sorted(yaml_files):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                if data := yaml.safe_load(f):
                    jsonl_file.write(json.dumps(data, ensure_ascii=False) + '\n')

    print(f"[INFO] train 파일 생성 완료: {train_file}")
except Exception as e:
    print(f"[ERROR] train 파일 생성 실패: {e}")

try:
    client = OpenAI()
    response = client.files.create(
        file=open(train_file, "rb"),
        purpose="fine-tune",
    )
    print("[INFO] train 파일 업로드 완료: ", response.id)
except Exception as e:
    print("[ERROR] train 파일 업로드 실패: ", e)

################ val_data ###############
val_file = os.path.join(output_dir, f'{current_date}-sft-val.jsonl')
val_data_dir = os.path.join(script_dir, 'data/val')
try:
    # YAML 파일 패턴들
    val_data_patterns = [
        os.path.join(val_data_dir, '*.yaml'),
        os.path.join(val_data_dir, '*.yml')
    ]

    yaml_files = []
    for pattern in val_data_patterns:
        yaml_files.extend(glob.glob(pattern))

    with open(val_file, 'w', encoding='utf-8') as jsonl_file:
        for yaml_file in sorted(yaml_files):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                if data := yaml.safe_load(f):
                    jsonl_file.write(json.dumps(data, ensure_ascii=False) + '\n')

    print(f"[INFO] val 파일 생성 완료: {val_file}")
except Exception as e:
    print(f"[ERROR] val 파일 생성 실패: {e}")

try:
    client = OpenAI()
    response = client.files.create(
        file=open(val_file, "rb"),
        purpose="fine-tune",
    )
    print("[INFO] val 파일 업로드 완료: ", response.id)
except Exception as e:
    print("[ERROR] val 파일 업로드 실패: ", e)
