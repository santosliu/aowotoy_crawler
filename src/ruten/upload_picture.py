"""
    將對應的圖片上傳到指定露天商品中

    1. 查詢資料庫中已經上傳的紀錄
    2. 取得指定位置的圖片並且上傳
    3. 更新資料庫內關於圖片上傳的紀錄欄位
    
"""

import os
import sys
import time
import requests
import logging
import json # 新增 json 模組
from dotenv import load_dotenv
from src.utils.db import getProductsWithoutPicture, setProductWithPictureCount


# 將專案根目錄添加到 Python 模組搜索路徑
# 這樣可以確保在任何位置執行腳本時，都能正確導入 src 模組
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, project_root)

from src.utils.common import genSign_compact 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    
    logging.info('開始進行 upload_picture。')

    load_dotenv() 

    url = 'https://partner.ruten.com.tw/api/v1/product/item/image'
    
    api_key = os.getenv('RUTEN_API_KEY')
    timestamp = str(int(time.time()))
    user_agent = os.getenv('RUTEN_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')


    # 取得已經上架但是還沒上圖片的項目
    ruten_id, product_id = getProductsWithoutPicture()
    
    # 如果 ruten_id 不為 null
    

    payload = {
        'item_id': ruten_id
    }

    # 取得 product_id 底下的圖片資料
    files = []
    
    products_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'products', str(product_id))
    image_files = [f for f in os.listdir(products_dir) if os.path.isfile(os.path.join(products_dir, f))]

    for image_file in image_files:
        file_path = os.path.join(products_dir, image_file)        
        mime_type = 'image/png' if image_file.lower().endswith('.png') else 'image/jpeg'
        files.append(('images[]', (image_file, open(file_path, 'rb'), mime_type)))

    sign_bytes = genSign_compact(url, payload, timestamp)

    headers = {
        'User-Agent' : user_agent,
        'X-RT-Timestamp': timestamp,
        'X-RT-Key': api_key,
        'X-RT-Authorization': sign_bytes
    }

    logging.info(f'正在向 {url} 發送請求...')
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    logging.info(f'收到回應: {response.text}')

    # 解析 JSON 字串
    response_data = json.loads(response.text)
    
    # 取得 success_images 的值
    success_images_count = response_data['data']['success_images']
    logging.info(f'成功上傳圖片數量: {success_images_count}')

    # 回寫資訊到 db
    setProductWithPictureCount(product_id, success_images_count)
    
    logging.info('腳本執行結束。')
