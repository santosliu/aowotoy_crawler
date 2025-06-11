import os
import hashlib
import hmac
import json
import time
import requests
from dotenv import load_dotenv

def genSign(salt_key, url, request_body, timestamp) -> str:

    # 將 request_body 轉換為 JSON 字符串
    request_body_json = json.dumps(request_body, separators=(',', ':'))

    # 準備計算簽名的數據
    # 將 timestamp 轉換為字串，以便與其他字串進行串聯
    data_for_sign = salt_key + url + request_body_json + timestamp

    # 計算 HMAC-SHA256 簽名
    # secret_key 已經是 bytes 類型，無需再次編碼
    sign_bytes = hmac.new(secret_key, data_for_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # 打印簽名結果
    return sign_bytes
    
if __name__ == '__main__':

    load_dotenv() 

    url = 'https://partner.ruten.com.tw/api/v1/product/item/image'
    
    api_key = os.getenv('RUTEN_API_KEY')
    secret_key = os.getenv('RUTEN_SECRET_KEY', '').encode('utf-8') # 強制轉換為 bytes
    salt_key = os.getenv('RUTEN_SALT_KEY', '') # 提供預設空字串，避免 None
    timestamp = str(int(time.time()))
    user_agent = os.getenv('RUTEN_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    payload = {
        'item_id': '22523758244600'
    }

    files=[
    ('images[]',('test1.png',open('doc/pic/test1.png','rb'),'image/png')),
    ('images[]', ('test2.jpg', open('doc/pic/test2.jpg', 'rb'), 'image/jpeg')),
    ]

    sign_bytes = genSign(salt_key, url, payload, timestamp)

    print(sign_bytes)

    headers = {
        'User-Agent' : user_agent,
        'X-RT-Timestamp': timestamp,
        'X-RT-Key': api_key,
        'X-RT-Authorization': sign_bytes
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)
