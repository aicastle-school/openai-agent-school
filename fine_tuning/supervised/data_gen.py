#!/usr/bin/env python3
import os
import yaml
import json
import base64
import glob
from pathlib import Path


def image_to_base64(image_path):
    """이미지 파일을 base64 문자열로 변환"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # 이미지 확장자에 따라 MIME 타입 결정
            ext = Path(image_path).suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            elif ext == '.gif':
                mime_type = 'image/gif'
            elif ext == '.webp':
                mime_type = 'image/webp'
            else:
                mime_type = 'image/png'  # 기본값
            
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"이미지 파일 읽기 오류 {image_path}: {e}")
        return None


def process_content(content, base_dir):
    """content에서 이미지 경로를 base64로 변환"""
    if isinstance(content, list):
        processed_content = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'image_url':
                image_url = item.get('image_url', {})
                if 'path' in image_url:
                    # 상대 경로를 절대 경로로 변환
                    image_path = os.path.join(base_dir, image_url['path'])
                    base64_url = image_to_base64(image_path)
                    if base64_url:
                        # path를 제거하고 url로 변경
                        new_item = item.copy()
                        new_item['image_url'] = {'url': base64_url}
                        processed_content.append(new_item)
                    else:
                        # base64 변환 실패시 원본 유지
                        processed_content.append(item)
                else:
                    processed_content.append(item)
            else:
                processed_content.append(item)
        return processed_content
    return content


def process_messages(messages, base_dir):
    """메시지 리스트에서 이미지 경로를 base64로 변환"""
    processed_messages = []
    for message in messages:
        processed_message = message.copy()
        if 'content' in message:
            processed_message['content'] = process_content(message['content'], base_dir)
        processed_messages.append(processed_message)
    return processed_messages


def yaml_to_jsonl():
    """data 폴더의 모든 YAML 파일을 JSONL로 변환"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    output_file = os.path.join(script_dir, 'data.jsonl')
    
    # YAML 파일 패턴들
    yaml_patterns = [
        os.path.join(data_dir, '*.yaml'),
        os.path.join(data_dir, '*.yml')
    ]
    
    yaml_files = []
    for pattern in yaml_patterns:
        yaml_files.extend(glob.glob(pattern))
    
    if not yaml_files:
        print(f"데이터 디렉토리에서 YAML 파일을 찾을 수 없습니다: {data_dir}")
        return
    
    print(f"발견된 YAML 파일들: {len(yaml_files)}개")
    
    with open(output_file, 'w', encoding='utf-8') as jsonl_file:
        for yaml_file in sorted(yaml_files):
            try:
                print(f"처리 중: {os.path.basename(yaml_file)}")
                
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                if not data:
                    print(f"빈 파일 스킵: {yaml_file}")
                    continue
                
                # 메시지에서 이미지 경로를 base64로 변환
                if 'messages' in data:
                    data['messages'] = process_messages(data['messages'], data_dir)
                
                # parallel_tool_calls 기본값 설정
                if 'tools' in data and 'parallel_tool_calls' not in data:
                    data['parallel_tool_calls'] = False
                
                # JSONL 형식으로 저장
                jsonl_file.write(json.dumps(data, ensure_ascii=False) + '\n')
                
            except Exception as e:
                print(f"파일 처리 오류 {yaml_file}: {e}")
                continue
    
    print(f"JSONL 파일이 생성되었습니다: {output_file}")


if __name__ == "__main__":
    yaml_to_jsonl()
