import os
import hashlib
import hmac
import json
from dotenv import load_dotenv

def genSign_compact(url: str, request_body: dict, timestamp: str) -> str:
    """
    根據露天 API 規範生成簽名。

    Args:
        salt_key (str): 露天 API 的 salt key。
        url (str): 請求的 URL。
        request_body (dict): 請求的 JSON 內容。
        timestamp (str): 時間戳。
        secret_key (bytes): 露天 API 的 secret key (bytes 類型)。

    Returns:
        str: 計算出的 HMAC-SHA256 簽名。
    """
    load_dotenv() 

    salt_key = os.getenv('RUTEN_SALT_KEY', '') # 提供預設空字串，避免 None
    secret_key = os.getenv('RUTEN_SECRET_KEY', '').encode('utf-8') # 強制轉換為 bytes
    
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

def genSign(url: str, request_body: dict, timestamp: str) -> str:
    """
    根據露天 API 規範生成簽名。

    Args:
        salt_key (str): 露天 API 的 salt key。
        url (str): 請求的 URL。
        request_body (dict): 請求的 JSON 內容。
        timestamp (str): 時間戳。
        secret_key (bytes): 露天 API 的 secret key (bytes 類型)。

    Returns:
        str: 計算出的 HMAC-SHA256 簽名。
    """
    load_dotenv() 

    salt_key = os.getenv('RUTEN_SALT_KEY', '') # 提供預設空字串，避免 None
    secret_key = os.getenv('RUTEN_SECRET_KEY', '').encode('utf-8') # 強制轉換為 bytes
    
    # 將 request_body 轉換為 JSON 字符串
    request_body_json = json.dumps(request_body)

    # 準備計算簽名的數據
    # 將 timestamp 轉換為字串，以便與其他字串進行串聯
    data_for_sign = salt_key + url + request_body_json + timestamp

    # 計算 HMAC-SHA256 簽名
    # secret_key 已經是 bytes 類型，無需再次編碼
    sign_bytes = hmac.new(secret_key, data_for_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # 打印簽名結果
    return sign_bytes
