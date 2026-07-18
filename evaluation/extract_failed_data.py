import json

def load_json(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def save_json(data, file_path):
    """保存数据到JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving JSON file: {e}")

def find_unique_items(a_data, b_data):
    """找到B中有而A中没有的message对应的项"""
    # 提取A中的所有message
    a_messages = {item['message'] for item in a_data if 'message' in item}
    
    # 找到B中message不在A中的项
    unique_items = [item for item in b_data if 'message' in item and item['message'] not in a_messages]
    
    return unique_items

def main():
    # 文件路径
    file_a = 'evaluation/results_gptfuzz/qwen2.5-turbo_attack_llama3.json'
    file_b = 'output/qwen2.5-turbo_gptfuzz_attack/qwen2.5-turbo_attack_Llama-3-8b-instruction.json'
    file_c = 'llama3.json'

    # 加载JSON文件
    data_a = load_json(file_a)
    data_b = load_json(file_b)

    if data_a is None or data_b is None:
        print("Failed to load one or both JSON files.")
        return

    # 找到B中有而A中没有的message对应的项
    unique_items = find_unique_items(data_a, data_b)

    # 保存结果到新的JSON文件
    save_json(unique_items, file_c)
    print(f"Unique items saved to {file_c}.")

if __name__ == "__main__":
    main()