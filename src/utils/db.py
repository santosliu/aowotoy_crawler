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
            WHERE ruten_id != 100 
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
            """

            # 測試用程式碼
            
            # 先上泡泡瑪特用
            # sql = """
            # SELECT  
            #     a.product_id AS product_id,
            #     a.option_id AS option_id,
            #     a.`name` AS product_name,
            #     a.summary AS summary,
            #     a.price AS price,
            #     a.`option` AS option_text,
            #     a.detail AS detail
            # FROM aowotoy_options as a
            # WHERE product_id = (
			# 	SELECT product_id 
            #     FROM aowotoy_products 
            #     WHERE url LIKE '%mart%' 
            #     AND ruten_id IS NULL                 
            #     LIMIT 1
			# 	)
            # """

            # sql = """
            # SELECT  
            #     a.product_id AS product_id,
            #     a.option_id AS option_id,
            #     a.`name` AS product_name,
            #     a.summary AS summary,
            #     a.price AS price,
            #     a.`option` AS option_text,
            #     a.detail AS detail
            # FROM aowotoy_options as a
            # WHERE product_id = '65b78bcb743dc700173b9745'
            # """

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

def getProductOptionsByProductId(product_id):
    """根據 product_id 取得產品選項資料"""
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor(dictionary=True)
            sql = """
            SELECT * FROM aowotoy_options
            WHERE product_id = %s
            """
            cursor.execute(sql, (product_id,))
            product_options_data = cursor.fetchall()
            if product_options_data:
                return product_options_data
            else:
                print(f"未找到產品 {product_id} 的選項資料。")
                return None
        else:
            print("無法連接到資料庫，無法獲取產品選項資料。")
            return None
    except mysql.connector.Error as err:
        print(f"從資料庫獲取產品選項資料失敗: {err}")
        return None
    except Exception as e:
        print(f"獲取產品選項資料時發生未知錯誤: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()

def setTaobaoProduct(products):
    """將多筆淘寶產品資料寫入資料庫"""
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor()
            sql = """
            INSERT INTO taobao_products (product_id, presale, product_url, product_name, feature_image, image_list)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                presale = VALUES(presale),
                product_url = VALUES(product_url),
                product_name = VALUES(product_name),
                feature_image = VALUES(feature_image),
                image_list = VALUES(image_list)
            """
            cursor.executemany(sql, products)
            mydb.commit()
            print(f"已成功寫入或更新 {cursor.rowcount} 筆產品資料。")
            return True
        else:
            print("無法連接到資料庫，無法寫入產品資料。")
            return False
    except mysql.connector.Error as err:
        print(f"寫入淘寶產品資料失敗: {err}")
        return False
    except Exception as e:
        print(f"寫入淘寶產品資料時發生未知錯誤: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()

def checkTaobaoProductID(product_id):
    """檢查淘寶 product_id 是否已存在於資料庫中"""
    mydb = None
    cursor = None
    try:
        mydb = connect_to_db()
        if mydb:
            cursor = mydb.cursor()
            sql = "SELECT COUNT(*) FROM taobao_products WHERE product_id = %s"
            cursor.execute(sql, (product_id,))
            result = cursor.fetchone()
            # 如果計數大於 0，表示 product_id 已存在
            if result[0] > 0:
                return True
            else:
                return False
        else:
            print("無法連接到資料庫，無法檢查產品 ID。")
            # 根據需求，這裡可以返回 True 以阻止後續操作，或引發異常
            return True
    except mysql.connector.Error as err:
        print(f"檢查淘寶產品 ID 時發生錯誤: {err}")
        return True
    except Exception as e:
        print(f"檢查淘寶產品 ID 時發生未知錯誤: {e}")
        return True
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()
