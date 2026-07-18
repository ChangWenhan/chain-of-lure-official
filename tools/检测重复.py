import json
from collections import Counter

def check_for_duplicates(json_file):
    try:
        # 读取 JSON 文件
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 提取所有 message 字段
        messages = [item.get("message", "") for item in json_data]

        # 使用 Counter 统计每个 message 的出现次数
        message_counts = Counter(messages)

        # 输出重复的 message
        duplicates = {msg: count for msg, count in message_counts.items() if count > 1}
        
        if duplicates:
            print("发现重复的 messages：")
            for msg, count in duplicates.items():
                print(f"Message: '{msg}' 出现了 {count} 次")
        else:
            print("没有重复的 messages。")

    except Exception as e:
        print(f"处理时发生错误: {e}")

# 调用主函数
if __name__ == "__main__":
    json_file = 'output/qwen2.5-turbo_attack/qwen2.5-turbo_attack_vicuna-7b-v1.5.json'  # 这里替换为你的 JSON 文件路径
    check_for_duplicates(json_file)
