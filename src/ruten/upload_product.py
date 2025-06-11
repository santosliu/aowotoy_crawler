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
from src.utils.common import genSign
from src.utils.db import get_unpublish_product, set_product_published

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
        # {"status":"success","data":{"item_id":"22523776659295","custom_no":"64f2172741270d001184247e"},"error_code":null,"error_msg":null}
        
        # 回寫至資料庫中備存
        try:
            data= json.loads(response.text)
            ruten_id = data.get("data", {}).get("item_id")
            product_id = data.get("data", {}).get("custom_no")

            set_product_published(product_id,ruten_id)
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

    products_to_upload = get_unpublish_product()

    store_class_id = '6529089'  # 預設為泡泡瑪特的 store_class_id
    if products_to_upload:
        logging.info("準備上傳以下產品資料:")
        for product in products_to_upload:
            # 根據產品名稱判斷 store_class_id
            store_class_id = '6529089' if '泡泡瑪特' in product['name'] else '6529088'

            # 解析 spec_info 欄位 (如果存在且為字串)
            spec_info_list = []
            if product.get('option') and isinstance(product['option'], str):
                spec_info_data = product['option']
                print(f"原始 spec_info_data: {spec_info_data}")



                try:
                    spec_info_data = json.loads(product['option'])
                    for spec in spec_info_data:
                        spec_info_list.append({
                            'spec_name': spec.get('spec_name', ''),
                            'item_name': spec.get('item_name', ''),
                            'status': spec.get('status', True), # 預設為 True
                            'price': spec.get('price', 0),
                            'qty': spec.get('qty', 0),
                            'custom_no': spec.get('custom_no', ''),
                        })
                except json.JSONDecodeError as e:
                    logging.error(f"解析 spec_info 失敗: {e} for product_id: {product.get('product_id')}")
                    spec_info_list = [] # 解析失敗則清空規格資訊

            
        # 構建上傳的產品資料字典
        product_data = {
            'name': product.get('name', ''),
            'class_id': '00050008', 
            'store_class_id': store_class_id,
            'condition': 1, 
            'stock_status': '21DAY', 
            'description': product.get('detail', ''),
            'video_link': '',
            'location_type': 1, # 預設為 1 (台灣)
            'location': '03', # 預設為 03 (新北市)
            'shipping_setting': 1, 
            'has_spec': bool(spec_info_list), # 如果 spec_info_list 不為空，則為 True
            'price': product.get('price', 0),
            'qty': 10,
            'custom_no': product.get('product_id', ''),
        }
        
        # 如果有規格，則添加 spec_info
        if spec_info_list:
            product_data['spec_info'] = spec_info_list
                
        logging.info(f"轉換後的產品資料: {json.dumps(product_data, ensure_ascii=False, indent=2)}")
        upload_product(product_data)

    else:
        logging.info("沒有產品資料可供上傳。")
