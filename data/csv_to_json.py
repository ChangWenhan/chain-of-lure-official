import csv
import json

def read_csv_column(file_path, column_name):
    """从CSV文件中读取指定列的数据"""
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if column_name in row:
                    data.append(row[column_name])
                else:
                    print(f"Warning: Column '{column_name}' not found in some rows.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return data

def save_to_json(data, file_path):
    """将数据保存到JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving JSON file: {e}")

def main():
    # 文件路径
    csv_file = 'data/gptfuzz.csv'  # 输入的CSV文件名
    json_file = 'data/gptfuzz.json'  # 输出的JSON文件名
    column_name = 'goal'  # 要读取的列名

    # 读取CSV文件中的目标列
    goal_data = read_csv_column(csv_file, column_name)

    if goal_data:
        # 将数据保存到JSON文件
        save_to_json(goal_data, json_file)
        print(f"Data from column '{column_name}' saved to {json_file}.")
    else:
        print("No data found or error occurred.")

if __name__ == "__main__":
    main()