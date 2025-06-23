import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import mysql.connector
from dotenv import load_dotenv
from src.utils.common import genSign, raisedPrice, replaceTitle, replaceDetail, replaceOption, getProductResponse
from src.utils.db import connect_to_db,getProductOptionsByProductId

# Load environment variables from .env file
load_dotenv()

# CSV file name
csv_file = 'shopee_goods.csv'

def delete_csv():
    """Traverse directories and delete all CSV files."""
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted existing file: {file_path}")
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}")

def export_all_csv(output_filename):
    conn = None
    try:
        # Connect to the database
        conn = connect_to_db()
        if not conn:
            print("無法連線到資料庫，匯出失敗。")
            return

        cursor = conn.cursor()

        cursor.execute("""
            SELECT product_id 
            FROM aowotoy_products            
            """)

        rows = cursor.fetchall()

        column_names = ['分類(A)', '商品名稱(B)', '商品描述(C)','最低購買數量(D)','主商品貨號(E)','規格貨號(F)','規格名稱(G)', '規格選項(H)', 
        '規格圖片(I)', '規格名稱 2(J)', '規格選項 2(K)', '價格(L)','庫存(M)', '商品選項貨號(N)', '新版尺寸表(O)', '圖片尺寸表(P)', 'GTIN(Q)', 
        '主商品圖片(R)', '商品圖片 1(S)', '商品圖片 2(T)', '商品圖片 3(U)', '商品圖片 4(V)', '商品圖片 5(W)', '商品圖片 6(X)', '商品圖片 7(Y)', 
        '商品圖片 8(Z)', '重量(AA)', '長度(AB)', '寬度(AC)', '高度(AD)', '黑貓宅急便(AE)', '蝦皮店到店(AF)', '新竹物流(AG)', '較長備貨天數(AH)']

        # Define the single CSV file path
        all_csv_file = output_filename

        with open(all_csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)

            # 輸出資料至 CSV
            for i, row in enumerate(rows):
                
                product_id = row[0]
                product_options_data = getProductOptionsByProductId(product_id)
                print(product_options_data)

                # for prodcut_options_data
                for option in product_options_data:

                    product_name = option['name']
                    
                    if product_name and ("解放玩具" in product_name):
                        print(f"產品名稱包含 '解放玩具'，跳過匯出：{product_name}")
                        continue 
                    
                    # 2025/06/24 處理到 option
                    option_value = option['option'] 
            
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
                        product_option = product_option.replace('only for Display Box, NOT include the exhibit+ ','')
                        product_option = product_option.replace('(只有展盒 不含模型)','')
                        
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

                    product_price = raisedPrice(option['price']) 
                    
                    
                    detail = option['detail']
                    option_id = option['option_id']

                    product_option = {}


                transformed_row = [
                    '101385',
                    replaceTitle(name),
                    replaceDetail(detail),
                    '1',
                    str(product_id),
                    '1', # F
                    option,
                    str(final_price),
                    '10',
                    '6438417',
                    f'專為 {name} 設計的壓克力公仔模型展示盒，附有噴繪背景與底板設計。\n\n商品材質：壓克力\n\n商品規格：{option}\n\n如有其他商品疑問，例如燈款、電源等，歡迎小窗詢問。',
                    '',
                    f'{product_id}_1.jpg',
                    f'{product_id}_2.jpg'
                ]

                # Write data to the single CSV file
                writer.writerow(transformed_row)

                print(f"Data for product {product_id} exported to {all_csv_file}")

        print(f"All product data exported to {all_csv_file}")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("資料庫連線已關閉。")

if __name__ == "__main__":
    delete_csv() 
    export_all_csv(output_filename='shopee_all_products.csv')
