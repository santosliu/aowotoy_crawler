import sys
import os

# 將專案根目錄添加到 Python 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import time
import hmac
import hashlib
import json
import requests
from dotenv import load_dotenv
import logging
from src.utils.db import connect_to_db
import mysql.connector

# 配置日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_product_data():
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)
            sql = "SELECT * FROM aowotoy_products WHERE product_id = '655ae4cca6e0d9001dcf8564'"
            cursor.execute(sql)
            product_data = cursor.fetchall()
            if product_data:
                logging.info(f"從資料庫獲取原始產品資料 (列表): {product_data}")
                # product_data 是列表，即使只有一條記錄，也需要取第一個元素
                # 返回所有產品資料列表
                return product_data
            else:
                logging.info("資料庫中沒有待上傳的產品資料。")
                return None
        else:
            logging.error("無法連接到資料庫，無法獲取產品資料。")
            return None
    except mysql.connector.Error as err:
        logging.error(f"從資料庫獲取產品資料失敗: {err}")
        return None
    except Exception as e:
        logging.error(f"獲取產品資料時發生未知錯誤: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()
            logging.info("資料庫連線已關閉。")

def upload_product(product_data: dict):
    load_dotenv() 

    url = 'https://partner.ruten.com.tw/api/v1/product/item/image'

    api_key = os.getenv('RUTEN_API_KEY')
    secret_key = os.getenv('RUTEN_SECRET_KEY')
    salt_key = os.getenv('RUTEN_SALT_KEY')
    timestamp = int(time.time()) 
    user_agent = os.getenv('RUTEN_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    post_body = json.dumps(product_data)

    message = (salt_key + url + post_body + str(timestamp)).encode('utf-8') # type: ignore
    signature = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256).hexdigest() # type: ignore

    headers = {
        'Content-Type': 'multipart/form-data',
        'User-Agent': user_agent,
        'X-RT-Key': api_key,
        'X-RT-Timestamp': str(timestamp), 
        'X-RT-Authorization': signature,
    }

    try:
        response = requests.post(url, json=product_data, headers=headers, timeout=10)
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
    
    product_data = {
        'item_id' : "22523758244600",        
    }
     
    upload_product(product_data)
