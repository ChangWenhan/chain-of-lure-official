import json
import pandas as pd

def check_message_in_goal(json_file, csv_file):
    try:
        # 读取 JSON 文件
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 读取 CSV 文件
        df = pd.read_csv(csv_file)
        
        if 'goal' not in df.columns:
            print("CSV 文件中没有 'goal' 列。")
            return
        
        # 检查 JSON 中的 message 是否出现在 CSV 的 goal 列中
        for i, item in enumerate(json_data):
            message = item.get("message", "")
            if message not in df['goal'].values:
                print(f"第 {i+1} 项: message '{message}' 不在 CSV 的 goal 列中")
        
        # 检查 CSV 中的 goal 是否出现在 JSON 的 message 字段中
        for i, goal in enumerate(df['goal']):
            if not any(goal == item.get("message", "") for item in json_data):
                print(f"CSV 第 {i+1} 行: goal '{goal}' 不在 JSON 的 message 字段中")
        
        print("检查完毕！")

    except Exception as e:
        print(f"处理时发生错误: {e}")

# 调用主函数
if __name__ == "__main__":
    json_file = 'output_story/Gemini-2-flash_attack_story.json'  # 这里替换为你的 JSON 文件路径
    csv_file = 'data/harmful_behaviors.csv'  # 这里替换为你的 CSV 文件路径
    check_message_in_goal(json_file, csv_file)