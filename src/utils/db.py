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

def get_products_without_picture():

    return ''

def set_product_pictured(product_id,ruten_id):

    return ''

def getProductsWithoutPublish():
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)
            sql = "SELECT * FROM aowotoy_products WHERE ruten_id is null LIMIT 2"
            cursor.execute(sql)
            product_data = cursor.fetchall()
            if product_data:                
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

def setProductPublished(ruten_id,product_id):

    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)
            sql = "UPDATE aowotoy_products SET ruten_id = %s WHERE product_id = %s"
            cursor.execute(sql, (ruten_id, product_id))
            mydb.commit()
            if cursor.rowcount > 0:
                print(f"產品 {product_id} 的 ruten_id 已更新為 {ruten_id}。")
                return True
            else:
                print(f"未找到產品 {product_id} 或 ruten_id 已是最新。")
                return False
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
