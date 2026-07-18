import json
import pandas as pd
import os

def remove_items_with_failure_reason(filepath: str):
    """
    Reads a JSON file, removes items where 'failure_reason' is present and not an empty string,
    and saves the modified data back to the original file.

    Args:
        filepath (str): The path to the JSON file.
    """
    try:
        # Open and load the JSON data from the file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Process data based on whether it's a list of items or a single dictionary item
        if isinstance(data, list):
            # Filter out items (dictionaries) that have a non-empty 'failure_reason'
            # An item is kept if:
            # 1. It's not a dictionary.
            # 2. It's a dictionary but does not have the 'failure_reason' key.
            # 3. It's a dictionary and has 'failure_reason', but the value is an empty string.
            filtered_data = [
                item for item in data
                if not (isinstance(item, dict) and item.get('failure_reason')) # .get() handles missing key gracefully and empty string is falsy
            ]
        elif isinstance(data, dict):
            # If the root of the JSON is a single dictionary,
            # check if it has a non-empty 'failure_reason'.
            # If it does, the entire dictionary (the single item) is effectively removed by replacing it with None or an empty dict.
            # Here, we choose to keep it only if 'failure_reason' is empty or not present.
            if data.get('failure_reason'): # If failure_reason exists and is not empty
                print(f"Warning: The root JSON object is a dictionary with a non-empty 'failure_reason'. The file will be emptied or an error might occur depending on desired behavior.")
                # Depending on desired behavior, you might want to make filtered_data = {} or raise an error.
                # For now, let's assume we clear it if the single root item has a failure.
                # Or, if the goal is to remove THE KEY, not the item:
                # if 'failure_reason' in data and data['failure_reason'] != "":
                #     del data['failure_reason']
                # filtered_data = data # then assign data back
                # Given the function name "remove_items", clearing it if it fails seems more aligned if root is the only item.
                # However, the original code did: filtered_data = {} if ('failure_reason' in data and data['failure_reason'] != "") else data
                # This means if the root object has a failure_reason, the entire file becomes an empty dictionary.
                filtered_data = {} if data.get('failure_reason') else data
            else:
                filtered_data = data
        else:
            # If the JSON data is not a list or a dictionary, it's an unsupported type for this operation
            print(f"Unsupported data type in JSON file '{filepath}'. Only lists or dictionaries are supported for filtering 'failure_reason'.")
            return

        # Write the filtered data back to the original file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully processed '{filepath}'. Items with non-empty 'failure_reason' were removed (if any).")

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' is not a valid JSON format.")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")

def find_and_save_missing_messages(json_filepath: str, csv_filepath: str):
    """
    Finds messages ("goal" column in CSV) that are present in a CSV file
    but not in a JSON file (as "message" field).
    Saves these missing messages (along with their "target" value from CSV)
    to a new CSV file.

    Args:
        json_filepath (str): Path to the JSON file.
        csv_filepath (str): Path to the CSV file (must contain 'goal' and 'target' columns).
    """
    try:
        # --- Load messages from JSON file ---
        json_messages = set() # Use a set for efficient 'in' checks
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: JSON file '{json_filepath}' not found.")
            return
        except json.JSONDecodeError:
            print(f"Error: JSON file '{json_filepath}' is not a valid JSON format.")
            return

        if isinstance(json_data, list):
            # Iterate through items if JSON data is a list
            for item in json_data:
                if isinstance(item, dict) and 'message' in item:
                    json_messages.add(str(item['message'])) # Ensure message is string for comparison
        elif isinstance(json_data, dict):
            # Handle case where JSON data is a single dictionary
            if 'message' in json_data:
                json_messages.add(str(json_data['message'])) # Ensure message is string
        else:
            print(f"Unsupported data type in JSON file '{json_filepath}'. Expected a list or a dictionary.")
            return

        # --- Load goals from CSV file ---
        try:
            df = pd.read_csv(csv_filepath)
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_filepath}' not found.")
            return
        except pd.errors.EmptyDataError:
            print(f"Error: CSV file '{csv_filepath}' is empty or has incorrect format.")
            return
        except Exception as e:
            print(f"Error reading CSV file '{csv_filepath}': {e}")
            return

        # Check for required columns in the CSV
        if 'goal' not in df.columns or 'target' not in df.columns:
            print(f"Error: CSV file '{csv_filepath}' must contain 'goal' and 'target' columns.")
            return

        # Prepare CSV data: select 'goal', 'target' and drop rows where either is missing
        csv_data_subset = df[['goal', 'target']].copy() # Use .copy() to avoid SettingWithCopyWarning
        csv_data_subset.dropna(subset=['goal', 'target'], inplace=True)
        
        # Ensure 'goal' column is treated as string for comparison
        csv_data_subset['goal'] = csv_data_subset['goal'].astype(str)

        # --- Find missing messages ---
        # Filter CSV data to find rows where 'goal' is not in json_messages
        missing_data_df = csv_data_subset[~csv_data_subset['goal'].isin(json_messages)]

        if missing_data_df.empty:
            print(f"All 'goal' messages from '{csv_filepath}' are present in '{json_filepath}'. No new file created.")
            return

        # --- Save missing messages to a new CSV file ---
        # Generate the output CSV filename based on the JSON filename's prefix
        json_filename_basename = os.path.basename(json_filepath)
        
        # Attempt to create a meaningful prefix for the new CSV file.
        # This part assumes a specific naming convention for the JSON file.
        # Example: "qwen2.5-turbo_attack_story_2.json" -> prefix "qwen2.5-turbo_attack"
        name_parts = json_filename_basename.split("story")
        if len(name_parts) > 0:
            prefix = name_parts[0].strip('_') # Remove trailing underscores from the prefix
        else:
            prefix = os.path.splitext(json_filename_basename)[0] # Fallback to filename without extension

        # Define the path for the new CSV file containing missing messages
        output_csv_filename = f"{prefix}_missing_messages.csv"
        output_csv_filepath = os.path.join(os.path.dirname(json_filepath), output_csv_filename) # Save in same dir as JSON

        missing_data_df.to_csv(output_csv_filepath, index=False, encoding='utf-8')
        print(f"Successfully saved {len(missing_data_df)} missing messages to '{output_csv_filepath}'.")

    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred in find_and_save_missing_messages: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    # Define file paths
    # Ensure these paths are correct and the files exist where expected.
    # Example JSON file path
    json_file_to_process = "attack_story/story_set_b/qwen2.5-turbo_attack_story_2.json"
    # Example CSV file path (source of all possible goals)
    source_csv_file = "data/harmful_behaviors.csv"

    # --- First Function Example: Remove items with failure_reason ---
    # This operation modifies the JSON file in place.
    # Make sure you have a backup if the original content is critical.
    # remove_items_with_failure_reason(json_file_to_process)

    # --- Second Function Example: Find missing messages ---
    # This creates a new CSV file with messages present in source_csv_file
    # but not in json_file_to_process.
    
    # Ensure the directories for output exist or are created if necessary
    # For example, if json_file_to_process is in a subdirectory, that subdir should exist.
    # os.makedirs(os.path.dirname(json_file_to_process), exist_ok=True) # If needed

    find_and_save_missing_messages(json_filepath=json_file_to_process, csv_filepath=source_csv_file)