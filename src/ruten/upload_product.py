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

    try:
        response = requests.post(url, json=product_data, headers=headers)
        response.raise_for_status() 
        logging.info(f"Product upload successful: {response.text}")
        
        # {"status":"success","data":{"item_id":"22524817576560","spec_info":[{"spec_id":"252400861778864","custom_no":"655ae4cc17325d001ea2620b","spec_name":"\u7121\u71c8\u539a\u5e95\u7248","item_name":""},{"spec_id":"252400861778875","custom_no":"655ae4cc17325d001ea2620c","spec_name":"\u9802\u5e95\u71c8\u7248","item_name":""}]},"error_code":null,"error_msg":null}        
        # 回寫至資料庫中備存
        ruten_id, product_id = getProductResponse(response.text)

        try:
            data= json.loads(response.text)
            ruten_id = data.get("data", {}).get("item_id")
            product_id = data.get("data", {}).get("custom_no")
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
    # 示例產品資料
    # product_data = {
    #     'name': '阿庫力測試泡泡瑪特',
    #     'class_id': '00050008',
    #     'store_class_id': '6529089', # 泡泡瑪特的全丟到泡泡瑪特(6529089)，其他可以全丟到公仔模型(6529088)
    #     'condition': 1,
    #     'stock_status': '21DAY',
    #     'description': '此為測試品項，之後請刪除',
    #     'video_link': '',
    #     'location_type': 1,
    #     'location': '03',
    #     'shipping_setting': 1,
    #     'has_spec': False, 
    #     'price': 99999999,
    #     'qty': 10,
    #     'custom_no': '6594da97bbd776001127a5',
    #     'has_spec': True,
    #     'spec_info':[
    #         {
    #             'spec_name': '互卡拼裝',
    #             'item_name': '背底圖案噴繪',
    #             'status': True,
    #             'price': 99999991,
    #             'qty': 10,
    #             'custom_no': '6594da97b9332a00126b08',
    #         },
    #         {
    #             'spec_name': '互卡拼裝',
    #             'item_name': '簡配透明盒身',
    #             'status': True,
    #             'price': 99999992,
    #             'qty': 10,
    #             'custom_no': '6594da97b9332a00126b09',
    #         },
    #         {
    #             'spec_name': '無需拼裝',
    #             'item_name': '背底圖案噴繪',
    #             'status': True,
    #             'price': 99999993,
    #             'qty': 10,
    #             'custom_no': '6594da97b9332a00126b0a',
    #         },
    #         {
    #             'spec_name': '無需拼裝',
    #             'item_name': '簡配透明盒身',
    #             'status': True,
    #             'price': 99999993,
    #             'qty': 10,
    #             'custom_no': '6594da97b9332a00126b0b',
    #         }
    #     ]
    # }

    # upload_product(product_data)

    ##### 以上為測試用 #####


    """

    以下不用上架

    選項有 無需拼裝一體式
    選項有 無需拼裝
    選項有 透明無噴繪
    標題 有「預售」
    標題 有「解放玩具」

    找到之後回寫錯誤狀態

    """

    products_to_upload = getProductsWithoutPublish()
    print(products_to_upload)
    store_class_id = '6529089'  # 預設為泡泡瑪特的 store_class_id
    
    if products_to_upload:
        logging.info("準備上傳以下產品資料:")

        for item in products_to_upload:
            product = dict(item) # 顯式轉換為字典
            
            print(product)

            # 根據產品名稱處理行為
            # 檢查 'name' 鍵是否存在且其值不為 None
            product_name = product.get(b'name', b'').decode('utf-8') # 將鍵和預設值轉換為 bytes，並將結果解碼
            if product_name and ("預購" in product_name or "預售" in product_name or "解放玩具" in product_name):
                print(f"產品名稱包含 '預購' '預售' '解放玩具'，跳過匯出：{product_name}")
                continue # 使用 continue 跳過當前迴圈的剩餘部分，繼續下一個產品

            store_class_id = '6529089' if '泡泡瑪特' in product_name else '6529088' # 使用已解碼的 product_name
            product_price = raisedPrice(product.get(b'price', 0)) # 將鍵轉換為 bytes
            
            spec_info_list = [] # 為每個產品重置 spec_info_list

            # 這裡需要特別處理 product.get('option') 可能為 None 的情況
            option_value = product.get(b'option') # 鍵改回 bytes
            if option_value is not None: # 檢查是否為 None
                # 確保 option_value 是字串才進行 replace
                if isinstance(option_value, bytes): # 如果是 bytes，則解碼
                    product_option = option_value.decode('utf-8')
                else:
                    product_option = str(option_value) # 轉換為字串以防萬一

                product_option = product_option.replace('只售展盒，不含展品+ ','')
                print(f"當前 option: {product_option}")

                try:
                    spec_info_list.append({
                        'spec_name': replaceOption(product_option),
                        'status': True,
                        'price': product_price,
                        'qty': 10,
                        'custom_no': product.get(b'option_id', b'').decode('utf-8'), # 將鍵和預設值轉換為 bytes，並將結果解碼
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
            'description': replaceDetail(product.get(b'detail', b'').decode('utf-8')), # 將鍵和預設值轉換為 bytes，並將結果解碼
            'video_link': '',
            'location_type': 1, # 預設為 1 (台灣)
            'location': '03', # 預設為 03 (新北市)
            'shipping_setting': 1, 
            'has_spec': bool(spec_info_list), # 如果 spec_info_list 不為空，則為 True
            'price': product.get(b'price', 0), # 將鍵轉換為 bytes
            'qty': 10,
            'custom_no': product.get(b'product_id', b'').decode('utf-8'), # 將鍵和預設值轉換為 bytes，並將結果解碼
        }
            
        # 如果有規格，則添加 spec_info
        if spec_info_list:
            product_data['spec_info'] = spec_info_list
                    
        logging.info(f"轉換後的產品資料: {json.dumps(product_data, ensure_ascii=False, indent=2)}")
        # upload_product(product_data) # 在迴圈內部呼叫 upload_product
    else:
        logging.info("沒有產品資料可供上傳。")
