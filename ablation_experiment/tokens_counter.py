import os
import json
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """计算给定文本的 token 数量"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def process_json_files(folder_path: str, model: str = "gpt-4"):
    """按顺序读取文件夹下的所有 JSON 文件，并计算每个文件中 'story' 字段的平均 token 长度"""
    json_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])
    
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        token_counts = [count_tokens(item["story"], model) for item in data if "story" in item]
        avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
        
        print(f"File: {json_file}, Average Tokens in 'story': {avg_tokens:.2f}")

# 示例使用
folder_path = "attack_story/story_set_a"  # 替换为你的文件夹路径
process_json_files(folder_path)