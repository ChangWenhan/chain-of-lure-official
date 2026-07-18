import json

def extract_selected_fields(data):
    """提取 JSON 中的 goal, final_suffix, response 字段"""
    extracted_data = []
    for value in data.values():
        if isinstance(value, dict):
            extracted_data.append({
                "message": value.get("goal"),
                "final_suffix": value.get("final_suffix"),
                "response": value.get("final_respond"),
            })
    return extracted_data

def main():
    json_file = "compare_methods/AutoDAN/mistral_gptfuzz_normal.json"  # 你的 JSON 文件路径
    output_file = "compare_methods/AutoDAN/gptfuzz_mistral_normal.json"  # 过滤后的 JSON 文件路径
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    filtered_data = extract_selected_fields(data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    
    print(f"已成功保存筛选后的数据到 {output_file}")

if __name__ == "__main__":
    main()