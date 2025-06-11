import json

def parse_json_data(json_string):
    """
    解析 JSON 字串並提取 item_id 和 custom_no。

    Args:
        json_string (str): 包含 item_id 和 custom_no 的 JSON 字串。

    Returns:
        tuple: 包含 item_id 和 custom_no 的元組，如果解析失敗則返回 (None, None)。
    """
    try:
        data = json.loads(json_string)
        item_id = data.get("data", {}).get("item_id")
        custom_no = data.get("data", {}).get("custom_no")
        return item_id, custom_no
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        return None, None
    except AttributeError as e:
        print(f"屬性錯誤 (可能 JSON 結構不符): {e}")
        return None, None

if __name__ == "__main__":
    json_data = '{"status":"success","data":{"item_id":"22523776659295","custom_no":"64f2172741270d001184247e"},"error_code":null,"error_msg":null}'
    
    item_id, custom_no = parse_json_data(json_data)

    if item_id and custom_no:
        print(f"item_id: {item_id}")
        print(f"custom_no: {custom_no}")
    else:
        print("無法提取 item_id 或 custom_no。")
