import os
import json

def merge_taobao_json():
    """
    Merges all Taobao JSON data from the '/json' directory into a single file
    in the root directory, checking for and reporting duplicates.

    This function reads all '.json' files from the '/json' directory,
    extracts the list of items under the 'data.data' key from each file,
    and combines them into a single list of unique items. If duplicate items are found
    (based on 'itemId'), their titles are printed to the console. The resulting unique
    list is then written to 'taobao.json' in the root directory with UTF-8 encoding
    and formatted for readability.
    """
    json_dir = 'json'
    output_file = 'taobao.json'
    unique_data = []
    seen_item_ids = set()

    # Delete the old output file if it exists
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"Removed old file: {output_file}")
        except Exception as e:
            print(f"Error removing old file {output_file}: {e}")
            return

    # Ensure the json directory exists
    if not os.path.isdir(json_dir):
        print(f"Error: Directory '{json_dir}' not found.")
        return

    for filename in os.listdir(json_dir):
        if filename.endswith('.json') and filename != 'taobao.json':
            filepath = os.path.join(json_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    # Extract data from the expected structure
                    if 'data' in content and 'data' in content['data']:
                        items = content['data']['data']
                        for item in items:
                            item_id = item.get('itemId')
                            if item_id:
                                if item_id in seen_item_ids:
                                    print(f"Duplicate item found: {item.get('title', 'No Title')}")
                                else:
                                    seen_item_ids.add(item_id)
                                    unique_data.append(item)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {filename}")
            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")

    # Write the combined unique data to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully merged {len(unique_data)} unique items into {output_file}")
    except Exception as e:
        print(f"An error occurred while writing to {output_file}: {e}")

if __name__ == '__main__':
    merge_taobao_json()
