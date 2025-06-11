import csv
import os
import re
import mysql.connector
from src.utils.common import raisedPrice,replaceTitle,replaceDetail,replaceOption
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CSV file name
csv_file = 'jolly.csv'

def connect_to_db():
    """建立並返回資料庫連線"""
    try:
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        # print("資料庫連線成功。")
        return mydb
    except mysql.connector.Error as err:
        print(f"資料庫連線失敗：{err}")
        return None

def check_csv():
    """刪除舊的 CSV 檔案並創建一個新的空檔案。"""
    csv_path = os.path.join('doc', csv_file)
    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
            print(f"已刪除舊檔案: {csv_path}")
        except OSError as e:
            print(f"刪除檔案 {csv_path} 時發生錯誤: {e}")
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            pass  # 創建一個空檔案
        print(f"已創建新檔案: {csv_path}")
    except IOError as e:
        print(f"創建檔案 {csv_path} 時發生錯誤: {e}")

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

def export_csv_by_product_id(product_id):
    
    
    product_id_val = ''
    product_name = ''
    product_price = ''
    preset_price = 0
    product_detail = ''
    options = {}

    conn = None
    try:
        # Connect to the database
        conn = connect_to_db()
        if not conn:
            print("無法連線到資料庫，匯出失敗。")
            return

        cursor = conn.cursor()

        cursor.execute("SELECT name, price, option , detail FROM aowotoy_options WHERE product_id = %s", (product_id,))

        rows = cursor.fetchall()

        # 印出 rows for debugging
        if rows:
            for row in rows:
                product_name = str(row[0]) if row[0] is not None else ''
                try:
                    product_price = float(row[1]) if row[1] is not None else 0.0
                except (ValueError, TypeError):
                    product_price = 0.0 # Default to 0.0 if conversion fails
                product_option = str(row[2]) if row[2] is not None else ''
                product_detail = str(row[3]) if row[3] is not None else ''
                
                product_option = product_option.replace('只售展盒，不含展品', '').replace('+', '').replace(' ','')
                
                # 按照要求提高價格到 1.6 倍並取整到最接近的 10 的倍數
                final_price = raisedPrice(product_price)

                # 把 product_option 和 final_price 置入 options
                options[product_option] = final_price
                preset_price = final_price
                
        else:
            print(f"No data fetched for product_id {product_id}.")
            return # 如果沒有抓到資料，則直接返回

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            # print("資料庫連線已關閉。")

    # 如果 product_name 有 預購 或者 解放玩具 就跳出
    if "預購" in product_name or"預售" in product_name or "解放玩具" in product_name:
        # print(f"產品名稱包含 '預購' '預售' '解放玩具'，跳過匯出：{product_name}")
        return

    # 取代文字
    product_name = replaceTitle(product_name)
    product_detail = replaceDetail(product_detail)
    
    total_count = len(options)*10

    row = f'172130,{product_name},{preset_price},,,{total_count},,,1,0,,2,2,,壓克力展示盒（Aowobox）,"◇不含公仔、模型、徽章等內容物，僅販售展示盒唷\n◇可根據您的特殊需求進行客製化與設計，有訂製需求的話可透過聊聊詢問\n◇有任何疑問都可以直接洽詢客服\n◇如果架上沒有你想買的款式也可以直接聯絡詢問"'
    row += f',"{product_detail}","展示盒,Aowobox,艾窩玩具,防塵盒",,'

    # 製作 images 字串
    image_count = get_image_count(product_id)
    image_urls = []
    for i in range(1, 7):
        if (i <= image_count):
            image_urls.append(f"https://images.gameqb.net/{product_id}/{product_id}_{i:04d}.jpg")
        else:
            image_urls.append(" ")
    
    row += ','.join(image_urls)
    row += ',,燈箱款式,,'

    # 印出 options
    for option, price in options.items():
        if "無需拼裝" in option or "透明無噴繪" in option:
            # print(f"品項名稱包含 '無需拼裝' 或 '透明無噴繪'，跳過：{option}")
            break
        
        option = replaceOption(option)        

        option_string = f",10,,{option},,{price},,"
        row += option_string

    # 打開 jolly.csv 並且 append 進入    
    csv_path = os.path.join('doc', csv_file)
    try:
        with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
            f.write(row + '\n')
        # print(f"產品 ID {product_id} 的資料已成功匯出到 {csv_path}")
    except IOError as e:
        print(f"寫入檔案 {csv_path} 時發生錯誤: {e}")

def get_products():
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            print("無法連線到資料庫，獲取產品ID失敗。")
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM aowotoy_products")
        products = [row[0] for row in cursor.fetchall()]
        return products
    except mysql.connector.Error as e:
        print(f"資料庫錯誤：{e}")
        return []
    except Exception as e:
        print(f"發生錯誤：{e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("資料庫連線已關閉。")

if __name__ == "__main__":
    check_csv() 
    
    products = get_products()
    count = 0
    for product_id in products:
        # if count >= 3:
        #     print("已匯出 3 個產品，跳出迴圈。")
        #     break
        export_csv_by_product_id(product_id)
        count += 1
