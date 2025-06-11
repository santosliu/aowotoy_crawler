import time
import hmac
import hashlib
import json
import requests
import os
from dotenv import load_dotenv
import logging

# 配置日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_picture(product_data: dict, image_paths: list[str]):
    load_dotenv() 

    url = 'https://partner.ruten.com.tw/api/v1/product/item/image'
    
    api_key = os.getenv('RUTEN_API_KEY')
    secret_key = os.getenv('RUTEN_SECRET_KEY')
    salt_key = os.getenv('RUTEN_SALT_KEY')
    timestamp = int(time.time()) 
    user_agent = os.getenv('RUTEN_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    # 檢查必要的環境變數是否已載入
    if not all([api_key, secret_key, salt_key]):
        logging.error("缺少必要的環境變數 (RUTEN_API_KEY, RUTEN_SECRET_KEY, RUTEN_SALT_KEY)。請檢查 .env 檔案。")
        return
    
    post_body = json.dumps(product_data)

    message = (salt_key + url + post_body + str(timestamp)).encode('utf-8')
    signature = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256).hexdigest()

    headers = {
        'User-Agent': user_agent,
        'X-RT-Key': api_key,
        'X-RT-Timestamp': str(timestamp), 
        'X-RT-Authorization': signature,
    }

    files = {}
    # 將 item_id 加入 product_data，並確保其為字串
    if 'item_id' in product_data:
        files['item_id'] = (None, str(product_data['item_id']))
    else:
        logging.error("product_data 字典中缺少 'item_id' 鍵。")
        return

    for index, path in enumerate(image_paths):
        try:
            # 嘗試從檔案路徑推斷 MIME 類型，如果失敗則使用 'application/octet-stream'
            import mimetypes
            mime_type, _ = mimetypes.guess_type(path)
            if mime_type is None:
                mime_type = ' multipart/form-data'

            # 取得檔案名稱
            file_name = os.path.basename(path)

            files[f'images[{index}]'] = (file_name, open(path, 'rb'), mime_type)
        except FileNotFoundError:
            logging.error(f"圖片檔案未找到: {path}")
            return
        except Exception as e:
            logging.error(f"處理圖片檔案 {path} 時發生錯誤: {e}")
            return

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        logging.info(f"Product upload successful: {response.text}")
        # {"status":"success","data":{"item_id":"22523776659295","custom_no":"64f2172741270d001184247e"},"error_code":null,"error_msg":null}
        # 這段要回寫到資料庫中備存
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Status Code: {e.response.status_code}")
            try:
                error_response_text = e.response.content.decode('utf-8', errors='ignore')
                error_data = json.loads(error_response_text)



                logging.error(f"Response JSON: {json.dumps(error_data, ensure_ascii=False, indent=2)}")


            except (UnicodeDecodeError, json.JSONDecodeError):
                logging.error(f"Response Text (raw): {e.response.content}")

if __name__ == '__main__':
    # 示例產品資料
    sample_product_data = {
        'item_id': '22523758244600'
    }
    # 圖片路徑列表
    sample_image_paths = [
        r'products/677783359167270001b48635/677783359167270001b48635_0001.jpg',
        r'products/677783359167270001b48635/677783359167270001b48635_0002.jpg',
    ]
    upload_picture(sample_product_data, sample_image_paths)
