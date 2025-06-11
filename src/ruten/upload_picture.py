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
from dotenv import load_dotenv

# 將專案根目錄添加到 Python 模組搜索路徑
# 這樣可以確保在任何位置執行腳本時，都能正確導入 src 模組
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, project_root)

from src.utils.common import genSign_compact # 從 common.py 導入 genSign 函數

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('腳本開始執行。')

    load_dotenv() 

    url = 'https://partner.ruten.com.tw/api/v1/product/item/image'
    
    api_key = os.getenv('RUTEN_API_KEY')
    timestamp = str(int(time.time()))
    user_agent = os.getenv('RUTEN_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    payload = {
        'item_id': '22523758244600'
    }

    files=[
    ('images[]',('test1.png',open('doc/pic/test1.png','rb'),'image/png')),
    ('images[]', ('test2.jpg', open('doc/pic/test2.jpg', 'rb'), 'image/jpeg')),
    ]

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
    logging.info('腳本執行結束。')
