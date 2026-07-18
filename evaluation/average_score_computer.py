import json

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def calculate_average_score(file_path):
    data = read_json_file(file_path)

    total_score = 0
    num_items = 0

    for item in data:
        score = item.get('score')  # 获取score字段
        if score is not None:  # 如果score存在
            total_score += int(score)
            num_items += 1

    if num_items == 0:
        print("没有找到有效的评分项！")
        return None
    
    average_score = total_score / num_items
    return average_score

# 调用函数，传入你的JSON文件路径
file_path = 'evaluation/results_advbench_reattack/results_deepseek_reattack_qwen-turbo-2025-04-28.json'  # 替换为你的文件路径
average_score = calculate_average_score(file_path)

if average_score is not None:
    print(f"所有项的平均分为: {average_score}")