import json

def find_failures(json_file_path):
    """
    Finds and returns items from a JSON file where 'failure_reason' is not empty.

    Args:
        json_file_path (str): The path to the JSON file.

    Returns:
        list: A list of dictionary items where 'failure_reason' is not empty.
                Returns an empty list if the file is not found or is invalid JSON.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file_path}'. Please ensure it's valid JSON.")
        return []

    failed_items = []
    # If the JSON is a list of objects
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("failure_reason"):
                failed_items.append(item)
    # If the JSON is a single object that might contain relevant keys
    elif isinstance(data, dict):
        # This part assumes a structure where 'failure_reason' might be at the top level
        # or within nested structures. You might need to adjust this depending on your JSON structure.
        if data.get("failure_reason"):
            failed_items.append(data)
        # You could add more sophisticated logic here to iterate through nested dictionaries
        # if your failure reasons are deeply embedded.

    return failed_items

# --- How to use it ---
# 1. Create a dummy JSON file for testing (e.g., 'data.json')
#    You can copy the example content below into a file named 'data.json' in the same directory as your Python script.

"""
[
    {
        "id": 1,
        "name": "Task A",
        "status": "completed",
        "failure_reason": ""
    },
    {
        "id": 2,
        "name": "Task B",
        "status": "failed",
        "failure_reason": "network timeout"
    },
    {
        "id": 3,
        "name": "Task C",
        "status": "pending",
        "failure_reason": null
    },
    {
        "id": 4,
        "name": "Task D",
        "status": "failed",
        "failure_reason": "authentication error"
    },
    {
        "id": 5,
        "name": "Task E",
        "status": "completed",
        "failure_reason": ""
    }
]
"""

# 2. Specify the path to your JSON file
json_file = 'attack_story/story_set_a/gpt2-attack-story-1.json' # Make sure this file exists with some content

# 3. Call the function
items_with_failures = find_failures(json_file)

# 4. Print the results
if items_with_failures:
    print("Items with non-empty 'failure_reason':")
    for item in items_with_failures:
        print(json.dumps(item, indent=4))
else:
    print("No items found with a non-empty 'failure_reason' or an error occurred.")