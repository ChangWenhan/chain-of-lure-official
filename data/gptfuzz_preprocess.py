import pandas as pd
import random

def modify_csv(input_file, output_file):
    # 读取 CSV 文件
    df = pd.read_csv(input_file)
    
    # 删除 index 列（如果存在）
    if 'index' in df.columns:
        df = df.drop(columns=['index'])
    
    # 修改 text 列表头为 goal
    if 'question' in df.columns:
        df = df.rename(columns={'question': 'goal'})
    
    # 生成 target 列
    prefixes = ["Sure, here is a guide for", "Sure, here is a tutorial for", "Sure, here is an outline for"]
    df['target'] = df['goal'].apply(lambda x: f"{random.choice(prefixes)} {x.lstrip()[0].lower() + x.lstrip()[1:] if x and x[0].isupper() else x}")
    
    # 保存修改后的 CSV 文件
    df.to_csv(output_file, index=False)

# 示例调用
modify_csv("data/forbidden_question_set.csv", "output.csv")