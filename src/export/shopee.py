import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import mysql.connector
from dotenv import load_dotenv
from src.utils.common import genSign, raisedPrice, replaceTitle, replaceShopeeDetail, replaceOption, getProductResponse
from src.utils.db import connect_to_db,getProductOptionsByProductId

# Load environment variables from .env file
load_dotenv()

# CSV file name
csv_file = 'shopee.csv'

def get_image_count(product_id):
    """抓取 /products/{product_id} 目錄底下的檔案數量。"""
    image_count = 0
    product_images_dir = os.path.join('products', str(product_id))
    if os.path.exists(product_images_dir) and os.path.isdir(product_images_dir):
        for item in os.listdir(product_images_dir):
            if os.path.isfile(os.path.join(product_images_dir, item)):
                image_count += 1
    else:
        print(f"目錄不存在或不是一個目錄: {product_images_dir}")
    return image_count

def delete_csv():
    output_dir = 'output'
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        for file in os.listdir(output_dir):
            if file.startswith('shopee_product_') and file.endswith('.csv'):
                file_path = os.path.join(output_dir, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted existing file: {file_path}")
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}")

def export_all_csv():
    conn = None
    current_csv_file = None
    writer = None
    f = None
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
            WHERE id > 7296         
            """)

        rows = cursor.fetchall()

        column_names = ['分類(A)', '商品名稱(B)', '商品描述(C)','最低購買數量(D)','主商品貨號(E)','規格貨號(F)','規格名稱(G)', '規格選項(H)', 
        '規格圖片(I)', '規格名稱 2(J)', '規格選項 2(K)', '價格(L)','庫存(M)', '商品選項貨號(N)', '新版尺寸表(O)', '圖片尺寸表(P)', 'GTIN(Q)', 
        '主商品圖片(R)', '商品圖片 1(S)', '商品圖片 2(T)', '商品圖片 3(U)', '商品圖片 4(V)', '商品圖片 5(W)', '商品圖片 6(X)', '商品圖片 7(Y)', 
        '商品圖片 8(Z)', '重量(AA)', '長度(AB)', '寬度(AC)', '高度(AD)', '黑貓宅急便(AE)', '蝦皮店到店(AF)', '新竹物流(AG)', '較長備貨天數(AH)']

        product_id_counter = 0
        file_batch_number = 1
        batch_size = 300
        
        product_serial = 0 

        # 輸出資料至 CSV
        for i, row in enumerate(rows):
            product_id = row[0]

            # Check if a new file needs to be created
            if product_id_counter % batch_size == 0:
                if f: # Close previous file if open
                    f.close()
                    print(f"Batch {file_batch_number-1} completed.")
                
                current_csv_file = os.path.join('output', f'shopee_product_{file_batch_number}.csv')
                f = open(current_csv_file, 'w', newline='', encoding='utf-8-sig')
                writer = csv.writer(f)
                writer.writerow(column_names)
                print(f"Starting new batch file: {current_csv_file}")
                file_batch_number += 1
                product_serial = 0 # Reset product_serial for each new file

            product_id_counter += 1
            product_serial = product_serial + 1
            
            spec_name = ''
            item_name = ''
            product_name = ''
            product_detail = ''

            product_options_data = getProductOptionsByProductId(product_id)
            
            if product_options_data is None:
                print(f"未找到產品 {product_id} 的選項資料。")
                continue
            
            for option in product_options_data:
                
                
                product_name = option['name']
                product_detail = option['detail']
                
                if product_name and ("解放玩具" in product_name):
                    print(f"產品名稱包含 '解放玩具'，跳過匯出：{product_name}")
                    continue 
                                    
                option_value = option['option'] 
                option_id = option['option_id']
                
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
                    if product_name and ("泡泡馬特" in product_name) and ('無燈厚底版' in product_option or '底1燈版(USB)' in product_option):
                        print(f'品項為泡泡瑪特，不上架「無燈厚底版」 與 「底1燈版(USB)」')
                        print(f'品項：{product_option}')
                        continue
                    
                    product_option = product_option.replace('只售展盒，不含展品+ ','')
                    product_option = product_option.replace('only for Display Box, NOT include the exhibit+ ','')
                    product_option = product_option.replace('(只有展盒 不含模型)','')
                    
                    transformed_row = [
                        '101385',
                        replaceTitle(product_name),
                        replaceShopeeDetail(product_detail),
                        '1',
                        str(product_id),
                        product_serial, # 同商品規格流水號(F)
                        '燈箱款式',
                        product_option,
                        '', # 首圖?(I)
                        '',
                        '',
                        raisedPrice(option['price']) , # 價格(L)
                        '10', # 庫存 (M)                        
                        option_id, # 商品選項貨號 (N)
                        '',
                        '',
                        '00',                                
                    ]

                    image_count = get_image_count(product_id)
                    
                    for img_idx in range(1, 7):
                        if (img_idx <= image_count):
                            transformed_row.append(f"https://images.gameqb.net/{product_id}/{product_id}_{img_idx:04d}.jpg")
                        else:
                            transformed_row.append("")

                    transformed_row.append("")
                    transformed_row.append("")
                    transformed_row.append("")
                    transformed_row.append("")
                    transformed_row.append("")
                    transformed_row.append("")
                    transformed_row.append("")
                    transformed_row.append("關閉")
                    transformed_row.append("關閉")
                    transformed_row.append("開啟")
                    transformed_row.append("20")

                    writer.writerow(transformed_row)

        if f: # Close the last file
            f.close()
            print(f"Last batch completed.")

        print(f"All product data exported in batches to the 'output' directory.")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("資料庫連線已關閉。")

if __name__ == "__main__":
    os.makedirs('output', exist_ok=True) # Ensure the output directory exists
    delete_csv() 
    export_all_csv()
