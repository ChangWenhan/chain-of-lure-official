import json
import os

def count_question_marks(text):
    """
    统计文本中问号 '?' 的数量。
    
    参数：
    - text (str): 输入的文本
    
    返回：
    - int: 问号的数量
    """
    return text.count('?')

def process_json_files(root_dir="output"):
    """
    遍历 output 目录下所有非 "victim" 开头的文件夹，并读取 "stage" 开头的 JSON 文件，
    计算每个文件中 story 字段的平均问号数。

    参数：
    - root_dir (str): 需要遍历的根目录
    """
    results = {}

    # 遍历 output 目录下的子文件夹
    for folder in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder)

        # 只处理非 "victim" 开头的文件夹
        if os.path.isdir(folder_path) and not folder.startswith("victim"):
            print(f"Processing folder: {folder}")

            # 遍历该文件夹下的所有 JSON 文件
            for filename in os.listdir(folder_path):
                if filename.startswith("stage") and filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)
                    print(f"  Reading file: {filename}")

                    # 读取 JSON 文件
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # 遍历 JSON 文件中的每一项，提取 "story" 字段
                    total_questions = 0
                    total_stories = 0
                    for item in data:
                        if isinstance(item, dict) and "story" in item:
                            story = item["story"]
                            question_count = count_question_marks(story)
                            total_questions += question_count
                            total_stories += 1

                    if total_stories > 0:
                        avg_questions = total_questions / total_stories
                        results[file_path] = avg_questions
                        print(f"  → Avg '?' per story: {avg_questions:.2f}")
                    else:
                        print(f"  Warning: No valid stories found in {filename}")

    return results

# 运行主函数
if __name__ == "__main__":
    results = process_json_files()
    print("\nFinal Results:")
    for file, avg_q in results.items():
        print(f"{file}: {avg_q:.2f}")
