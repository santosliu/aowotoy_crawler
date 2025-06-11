import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv() # 從 .env 文件載入環境變數

def connect_to_db():
    """建立並返回資料庫連線"""
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        print("資料庫連線成功。")
        return mydb
    except mysql.connector.Error as err:
        print(f"資料庫連線失敗：{err}")
        return None

def get_unpublish_product():
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)
            sql = "SELECT * FROM aowotoy_products WHERE product_id = '655ae4cca6e0d9001dcf8564'"
            cursor.execute(sql)
            product_data = cursor.fetchall()
            if product_data:
                print(f"從資料庫獲取原始產品資料 (列表): {product_data}")
                # product_data 是列表，即使只有一條記錄，也需要取第一個元素
                # 返回所有產品資料列表
                return product_data
            else:
                print("資料庫中沒有待上傳的產品資料。")
                return None
        else:
            print("無法連接到資料庫，無法獲取產品資料。")
            return None
    except mysql.connector.Error as err:
        print(f"從資料庫獲取產品資料失敗: {err}")
        return None
    except Exception as e:
        print(f"獲取產品資料時發生未知錯誤: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()
            print("資料庫連線已關閉。")
