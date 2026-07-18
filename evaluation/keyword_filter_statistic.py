import json

# 读取JSON文件
with open('compare_methods/GCG/nanoGCG_vicuna-7b-v1.5.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 统计"failure_reason"为空的项目数量
total_items = len(data)
failure_reason_empty = sum(1 for item in data if item.get('failure_reason') == "")

# 计算占比
if total_items > 0:
    print("成功条目：", failure_reason_empty)
    print("总条目：", total_items)
    ratio = failure_reason_empty / total_items
    print(f"占比为: {ratio:.2%}")
else:
    print("数据为空")

