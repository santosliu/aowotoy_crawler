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
        
        return mydb
    except mysql.connector.Error as err:
        print(f"資料庫連線失敗：{err}")
        return None

def getProductsWithoutPicture():

    """

    調整 SQL，每次只取得一個商品

    """
    
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)

            sql = """
            SELECT * FROM aowotoy_products
            WHERE ruten_id IS NOT NULL 
            AND image_counts IS NULL
            LIMIT 1
            """
            cursor.execute(sql)
            product_options_data = cursor.fetchall() 
            if product_options_data:
                ruten_id = product_options_data[0]['ruten_id']
                product_id = product_options_data[0]['product_id']

                return ruten_id, product_id
            else:
                print("資料庫中沒有待上傳的產品資料。")
                return None, None
        else:
            print("無法連接到資料庫，無法獲取產品資料。")
            return None, None
    except mysql.connector.Error as err:
        print(f"從資料庫獲取產品資料失敗: {err}")
        return None, None
    except Exception as e:
        print(f"獲取產品資料時發生未知錯誤: {e}")
        return None, None
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()

def setProductWithPictureCount(product_id,image_counts):

    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)
            sql = "UPDATE aowotoy_products SET image_counts = %s WHERE product_id = %s;"
            cursor.execute(sql, (image_counts, product_id))
            mydb.commit()
            if cursor.rowcount > 0:
                print(f"產品 {product_id} 的圖片數量已更新為 {image_counts}。")
                return True
            else:
                print(f"未找到產品 {product_id} 或所有商品皆上圖完畢。")
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

def getProductsWithoutPublish():
    """

    調整 SQL，每次只取得一個商品

    """
    
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)

            sql = """
            SELECT 
                a.product_id AS product_id,
                a.option_id AS option_id,
                a.`name` AS product_name,
                a.summary AS summary,
                a.price AS price,
                a.`option` AS option_text,
                a.detail AS detail
            FROM aowotoy_options AS a
            INNER JOIN aowotoy_products AS b
                ON a.product_id = b.product_id
            WHERE b.ruten_id IS NULL
                AND a.product_id = (
                    SELECT MIN(product_id) 
                    FROM aowotoy_products 
                    WHERE ruten_id IS NULL
                );
            ;
            """

            # 測試用程式碼
            
            sql = """
            SELECT  
                a.product_id AS product_id,
                a.option_id AS option_id,
                a.`name` AS product_name,
                a.summary AS summary,
                a.price AS price,
                a.`option` AS option_text,
                a.detail AS detail
            FROM aowotoy_options as a
            WHERE product_id = '6562fbc103b565000e2bbc83'
            """

            cursor.execute(sql)
            product_options_data = cursor.fetchall() 
            if product_options_data:                
                return product_options_data
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

def setProductPublished(product_id,ruten_id):
    
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)
            sql = "UPDATE aowotoy_products SET ruten_id = %s WHERE product_id = %s;"
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
