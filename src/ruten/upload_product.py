"""
    把資料庫的商品上傳到露天拍賣
    並且記錄下來以免重複上傳

    1. 查詢資料庫中尚未上傳的紀錄
    2. 編成正確的 json 
    3. 更新資料庫紀錄欄位
    
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import time
import json
import requests
import logging
from dotenv import load_dotenv
from src.utils.common import genSign, raisedPrice, replaceTitle, replaceDetail, replaceOption, getProductResponse
from src.utils.db import getProductsWithoutPublish,setProductPublished

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_product(product_data: dict):
    load_dotenv() 

    url = 'https://partner.ruten.com.tw/api/v1/product/item'

    api_key = os.getenv('RUTEN_API_KEY', '') # 提供預設空字串
    timestamp = str(int(time.time()))
    user_agent = os.getenv('RUTEN_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # 使用 genSign 函數生成簽名
    sign_bytes = genSign(url, product_data, str(timestamp))
    
    headers = {
        'User-Agent': user_agent,
        'X-RT-Key': api_key,
        'X-RT-Timestamp': timestamp, 
        'X-RT-Authorization': sign_bytes,
    }

    # print(f'product_data:{product_data['custom_no']}')

    try:
        response = requests.post(url, json=product_data, headers=headers)
        response.raise_for_status() 
        
        # 回寫至資料庫中備存
        ruten_id, product_id = getProductResponse(response.text)
        
        try:
            data= json.loads(response.text)
            ruten_id = data.get("data", {}).get("item_id")
            product_id = product_data['custom_no']
            
            setProductPublished(product_id,ruten_id)
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON 解析錯誤: {e}")
        
    except AttributeError as e:
        logging.error(f"屬性錯誤 (可能 JSON 結構不符): {e}")

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

    products_to_upload = getProductsWithoutPublish()
    
    spec_info_list = [] 

    if products_to_upload:
        logging.info("準備上傳以下產品資料:")

        for item in products_to_upload:
            
            product = item # 直接使用 item，因為它已經是字典或類似字典的對象
            
            # 根據產品名稱處理行為
            # 確保從字典中取出的值是字串類型，並將鍵轉換為 bytes
            product_name = str(product.get('product_name', ''))
            
            if product_name and ("預購" in product_name or "預售" in product_name or "解放玩具" in product_name):
                print(f"產品名稱包含 '預購' '預售' '解放玩具'，跳過匯出：{product_name}")
                continue # 使用 continue 跳過當前迴圈的剩餘部分，繼續下一個產品

            store_class_id = '6529089' if '泡泡瑪特' in product_name else '6529088' # 轉換類別
            product_price = raisedPrice(product.get('price')) 

            # 這裡需要特別處理 product.get('option_text') 可能為 None 的情況
            option_value = product.get('option_text') 
            
            if option_value is not None: # 檢查是否為 None
                # 確保 option_value 是字串才進行 replace
                if isinstance(option_value, bytes): # 如果是 bytes，則解碼
                    product_option = option_value.decode('utf-8')
                else:
                    product_option = str(option_value) # 轉換為字串以防萬一
                
                if ('無需拼裝' in product_option or '透明無噴繪' in product_option):
                    print(f'「無需拼裝」 與 「透明無噴繪」不上架')
                    continue

                # 只要是泡泡瑪特，就不上架 「無燈厚底版」 與 「底1燈版(USB)」
                if store_class_id == '6529089' and ('無燈厚底版' in product_option or '底1燈版(USB)' in product_option):
                    print(f'品項為泡泡瑪特，不上架「無燈厚底版」 與 「底1燈版(USB)」')
                    print(f'品項：{product_option}')
                    continue
                
                product_option = product_option.replace('只售展盒，不含展品+ ','')
                
                # 檢查 product_option 有沒有 + 號
                if '+' in product_option:
                    # 使用 + 號分隔 option
                    options = product_option.split('+')

                    # 我只要第一和第二個 option，分別命名為 spec_name 和 item_name
                    spec_name = options[0].strip()
                    item_name = options[1].strip()

                    try:
                        spec_info_list.append({
                            'spec_name': replaceOption(spec_name),
                            'item_name': replaceOption(item_name), 
                            'status': True,
                            'price': product_price,
                            'qty': 10,
                            'custom_no': str(product.get('option_id', '')), # 確保 custom_no 是字串
                        })
                            
                    except json.JSONDecodeError as e:
                        logging.error(f"解析失敗: {e}")


                else:
                    try:
                        spec_info_list.append({
                            'spec_name': replaceOption(product_option),
                            'status': True,
                            'price': product_price,
                            'qty': 10,
                            'custom_no': str(product.get('option_id', '')), # 確保 custom_no 是字串
                        })
                            
                    except json.JSONDecodeError as e:
                        logging.error(f"解析失敗: {e}")

        # 構建上傳的產品資料字典
        product_data = {
            'name': replaceTitle(product_name), # 使用已解碼的 product_name
            'class_id': '00050008', 
            'store_class_id': store_class_id,
            'condition': 1, 
            'stock_status': '21DAY', 
            'description': replaceDetail(str(product.get('detail', ''))), # 確保 detail 是字串
            'video_link': '',
            'location_type': 1, # 預設為 1 (台灣)
            'location': '03', # 預設為 03 (新北市)
            'shipping_setting': 1, 
            'has_spec': bool(spec_info_list), # 如果 spec_info_list 不為空，則為 True
            'price': product_price, 
            'qty': 10,
            'custom_no': str(product.get('product_id', '')), # 確保 custom_no 是字串
        }
            
        # 如果有規格，則添加 spec_info
        if spec_info_list:
            product_data['spec_info'] = spec_info_list

        logging.info(f"轉換後的產品資料: {json.dumps(product_data, ensure_ascii=False, indent=2)}")
        
        upload_product(product_data) 

    else:
        logging.info("沒有產品資料可供上傳。")
