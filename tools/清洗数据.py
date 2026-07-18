import json

def process_json_element(element):
    """
    递归地处理 JSON 元素。
    如果元素是一个字典并且包含一个名为 'story' 的键，其值为字符串，
    则会尝试根据 "Scenario Description:" 修改 'story' 的内容。
    此函数会直接修改传入的元素（in-place）。
    """
    if isinstance(element, dict):
        # 检查当前字典是否包含 'story' 键，并且其值是否为字符串
        if "story" in element and isinstance(element["story"], str):
            story_text = element["story"]
            keyword = "**Scenario Description:**"
            index = story_text.find(keyword)
            if index != -1:
                # 如果找到关键字，则截取字符串
                element["story"] = story_text[index:]
        
        # 递归处理字典中的所有值
        # 即便当前字典自身被修改，其子元素也需要被检查
        for key in element:
            process_json_element(element[key]) # 递归调用，修改其值（如果是可变类型）

    elif isinstance(element, list):
        # 递归处理列表中的所有项
        for i in range(len(element)):
            process_json_element(element[i]) # 递归调用，修改列表中的项
    
    # 对于其他类型（如字符串、数字、布尔值等），不做任何操作
    # 因为它们是不可变类型，或者不符合修改条件


def modify_json_file_in_place(file_path):
    """
    读取指定的 JSON 文件，按要求修改 'story' 字段，
    然后将修改后的内容保存回原始文件。

    参数:
    file_path (str): 需要修改的 JSON 文件的路径。
    """
    try:
        # 1. 读取 JSON 文件内容到内存
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到。")
        return
    except json.JSONDecodeError:
        print(f"错误：文件 '{file_path}' 不是有效的 JSON 格式。请检查文件内容。")
        return
    except Exception as e:
        print(f"读取文件 '{file_path}' 时发生未知错误: {e}")
        return

    # 2. 处理加载到内存中的数据 (in-place modification)
    process_json_element(data)

    try:
        # 3. 将修改后的数据写回原始文件
        # 使用 'w' 模式会覆盖原文件内容
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False) # indent=4 使JSON文件更易读
        print(f"文件 '{file_path}' 已成功修改并保存。")
    except Exception as e:
        print(f"写入修改到文件 '{file_path}' 时发生错误: {e}")

# --- 如何使用 ---
if __name__ == '__main__':
    # 重要：此脚本会直接修改原始文件。
    # 强烈建议在对重要文件操作前先进行备份。
    
    # 请将下面的 'your_actual_file.json' 替换为你的JSON文件的实际路径和名称。
    # 例如: json_file_path = 'data/my_stories.json'
    # 或者在 Windows 上: json_file_path = r'C:\Users\YourUser\Documents\my_data.json'
    json_file_path = 'attack_story/story_set_gptfuzz/Gemma3-1B-attack-story.json' 

    if json_file_path == 'your_actual_file.json':
        print("请在脚本中修改 'json_file_path' 变量，")
        print("将其值设置为您要处理的实际JSON文件的路径，然后重新运行脚本。")
    else:
        # （可选）在实际操作前添加一个确认步骤，因为这是破坏性操作
        # confirm = input(f"您确定要修改文件 '{json_file_path}' 吗？此操作将覆盖原文件。(yes/no): ")
        # if confirm.lower() == 'yes':
        #     print(f"正在处理文件: {json_file_path}...")
        #     modify_json_file_in_place(json_file_path)
        # else:
        #     print("操作已取消。")
        
        # 如果不需要确认，直接运行：
        print(f"正在处理文件: {json_file_path}...")
        modify_json_file_in_place(json_file_path)