"""
    此模組用於存放露天拍賣 API 的共用設定。
"""

import os
from dotenv import load_dotenv

# 在模組載入時就載入環境變數，確保設定可用
load_dotenv()

class RutenConfig:
    """
        露天拍賣 API 的設定類別。
    """
    URL_BASE = 'https://partner.ruten.com.tw/api/v1'
    API_KEY = os.getenv('RUTEN_API_KEY')
    SECRET_KEY = os.getenv('RUTEN_SECRET_KEY', '').encode('utf-8')
    SALT_KEY = os.getenv('RUTEN_SALT_KEY', '')
    USER_AGENT = os.getenv('RUTEN_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    # 圖片上傳的特定 URL
    UPLOAD_IMAGE_URL = f'{URL_BASE}/product/item/image'

    # 其他 API 端點可以依此模式添加
    # GET_ITEM_LIST_URL = f'{URL_BASE}/product/item/list'
    # UPLOAD_PRODUCT_URL = f'{URL_BASE}/product/item'
