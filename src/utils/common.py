import os
import re
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

def raisedPrice(product_price):

    # 按照要求提高價格到 1.6 倍並取整到最接近的 10 的倍數
    calculated_price = round(product_price * 1.6)
    final_price = calculated_price - (calculated_price % 10)

    return final_price

def replaceTitle(product_name):

    product_name = product_name.replace('高達', '鋼彈')
    product_name = product_name.replace('手辦', '專用')
    product_name = product_name.replace('AOWOBOX', '阿庫力')
    product_name = product_name.replace('Good Smile', '好微笑')
    product_name = product_name.replace('良笑社', '')
    product_name = product_name.replace('高透主題展示盒', '主題展示盒')
    product_name = product_name.replace('高透射燈主題展示盒', '主題展示盒')    
    product_name = product_name.replace('\\u0026', '')

    return product_name


def replaceDetail(product_detail):

    product_detail = product_detail.replace('展示盒使用高達95%透光度的高透亮亞克力物料製造。主題高清噴繪設計背景，配上LED燈板，提升展品氛圍，同時免受塵封困擾', '')
    product_detail = re.sub(r'(.*+)同時免受塵封困擾', r'', product_detail)
    
    product_detail = product_detail.replace('brand:AOWOBOX', '')
    product_detail = product_detail.replace('brand:', '')
    product_detail = product_detail.replace('AOWOBOX', '')

    product_detail = product_detail.replace(' ', '')
    product_detail = product_detail.replace('高達', '鋼彈')
    product_detail = product_detail.replace('手辦', '專用')
    product_detail = product_detail.replace('AOWOBOX', '阿庫力')
    product_detail = product_detail.replace('Good Smile', '好微笑')
    product_detail = product_detail.replace('良笑社', '')
    product_detail = product_detail.replace('高透主題展示盒', '')
    product_detail = product_detail.replace('高透射燈主題展示盒', '')   
    product_detail = product_detail.replace('material', '材質')
    product_detail = product_detail.replace('powersupply', '電源')
    product_detail = product_detail.replace('款式選擇', '規格細節')
    product_detail = product_detail.replace(':', '：')

    # product_detail 使用 re 取代 
    # from size:W25 cm D20cm H30cm
    # to 尺寸: 長30cm 寬25cm 高45cm
    product_detail = product_detail.replace('size', '尺寸')   
    product_detail = product_detail.replace('Size', '尺寸')   
    product_detail = re.sub(r'W(\d+)cm', r'寬\1cm', product_detail)
    product_detail = re.sub(r'H(\d+)cm', r'高\1cm', product_detail)
    product_detail = re.sub(r'D(\d+)cm', r'長\1cm', product_detail)
    product_detail = re.sub(r'W(\d+)', r'寬\1', product_detail)
    product_detail = re.sub(r'H(\d+)', r'高\1', product_detail)
    product_detail = re.sub(r'D(\d+)', r'長\1', product_detail)
    product_detail = re.sub(r'鋼彈(\d+)%', r'高達\1%', product_detail)
    product_detail = product_detail.replace('cm','公分')
    product_detail = product_detail.replace('\t','')
    
    product_detail = re.sub(r'(<br\s*/?>\s*){3,}', '\n\n', product_detail, flags=re.IGNORECASE)
    product_detail = re.sub(r'.*同時免受塵封困擾\n', '', product_detail)

    final_detail = """📕請先閱讀注意事項再下單哦\n商品寄送需要等待清關，預計 20 天內會寄到您手上\n請一定要確認填寫資料的正確性，不然重寄會需要等待哦\n因為超商取貨有尺寸限制，所以只能透過宅配運送\n圖片是參考用的示意圖，不含裡面的公仔以及模型唷\n有什麼疑問都可以直接詢問\n如果覺得裝不起來記得先詢問，不要硬裝哦\n""" + product_detail

    return final_detail

def replaceShopeeDetail(product_detail):

    product_detail = product_detail.replace('展示盒使用高達95%透光度的高透亮亞克力物料製造。主題高清噴繪設計背景，配上LED燈板，提升展品氛圍，同時免受塵封困擾', '')
    product_detail = re.sub(r'(.*+)同時免受塵封困擾', r'', product_detail)
    
    product_detail = product_detail.replace('brand:AOWOBOX', '')
    product_detail = product_detail.replace('brand:', '')
    product_detail = product_detail.replace('AOWOBOX', '')

    product_detail = product_detail.replace(' ', '')
    product_detail = product_detail.replace('高達', '鋼彈')
    product_detail = product_detail.replace('手辦', '專用')
    product_detail = product_detail.replace('AOWOBOX', '阿庫力')
    product_detail = product_detail.replace('Good Smile', '好微笑')
    product_detail = product_detail.replace('良笑社', '')
    product_detail = product_detail.replace('高透主題展示盒', '')
    product_detail = product_detail.replace('高透射燈主題展示盒', '')   
    product_detail = product_detail.replace('material', '材質')
    product_detail = product_detail.replace('powersupply', '電源')
    product_detail = product_detail.replace('款式選擇', '規格細節')
    product_detail = product_detail.replace(':', '：')

    # product_detail 使用 re 取代 
    # from size:W25 cm D20cm H30cm
    # to 尺寸: 長30cm 寬25cm 高45cm
    product_detail = product_detail.replace('size', '尺寸')   
    product_detail = product_detail.replace('Size', '尺寸')   
    product_detail = re.sub(r'W(\d+)cm', r'寬\1cm', product_detail)
    product_detail = re.sub(r'H(\d+)cm', r'高\1cm', product_detail)
    product_detail = re.sub(r'D(\d+)cm', r'長\1cm', product_detail)
    product_detail = re.sub(r'W(\d+)', r'寬\1', product_detail)
    product_detail = re.sub(r'H(\d+)', r'高\1', product_detail)
    product_detail = re.sub(r'D(\d+)', r'長\1', product_detail)
    product_detail = re.sub(r'鋼彈(\d+)%', r'高達\1%', product_detail)
    product_detail = product_detail.replace('cm','公分')
    product_detail = product_detail.replace('\t','')
    product_detail = product_detail.replace('\n','<br/>')
    
    product_detail = re.sub(r'(<br\s*/?>\s*){3,}', '<br/><br/>', product_detail, flags=re.IGNORECASE)
    product_detail = re.sub(r'.*同時免受塵封困擾<br/>', '', product_detail)

    final_detail = """📕請先閱讀注意事項再下單哦\n商品寄送需要等待清關，預計 20 天內會寄到您手上\n請一定要確認填寫資料的正確性，不然重寄會需要等待哦\n因為超商取貨有尺寸限制，所以只能透過宅配運送\n圖片是參考用的示意圖，不含裡面的公仔以及模型唷\n有什麼疑問都可以直接詢問\n如果覺得裝不起來記得先詢問，不要硬裝哦</li></ol></div>""" + product_detail

    return final_detail

def replaceOption(option):

    option = re.sub(r'W(\d+)cm', r'寬\1cm', option)
    option = re.sub(r'H(\d+)cm', r'高\1cm', option)
    option = re.sub(r'D(\d+)cm', r'長\1cm', option)

    option = re.sub(r'W(\d+)', r'寬\1', option)
    option = re.sub(r'H(\d+)', r'高\1', option)
    option = re.sub(r'D(\d+)', r'長\1', option)

    option = option.replace('cm','公分')    

    return option

def getProductResponse(json_string):
    """
    解析 JSON 字串並提取 item_id 和 custom_no。

    Args:
        json_string (str): 包含 item_id 和 custom_no 的 JSON 字串。

    Returns:
        tuple: 包含 item_id 和 custom_no 的元組，如果解析失敗則返回 (None, None)。
    """
    try:
        data = json.loads(json_string)
        # {"status":"success","data":{"item_id":"22524817576560","spec_info":[{"spec_id":"252400861778864","custom_no":"655ae4cc17325d001ea2620b","spec_name":"\u7121\u71c8\u539a\u5e95\u7248","item_name":""},{"spec_id":"252400861778875","custom_no":"655ae4cc17325d001ea2620c","spec_name":"\u9802\u5e95\u71c8\u7248","item_name":""}]},"error_code":null,"error_msg":null}
        item_id = data.get("data", {}).get("item_id")
        custom_no = data.get("data", {}).get("custom_no")
        return item_id, custom_no
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        return None, None
    except AttributeError as e:
        print(f"屬性錯誤 (可能 JSON 結構不符): {e}")
        return None, None
