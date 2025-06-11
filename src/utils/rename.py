import os

def rename_images(products_dir="products"):
    for root, dirs, files in os.walk(products_dir):
        # 跳過基礎產品目錄本身，只處理子目錄（產品ID）
        if root == products_dir:
            continue

        product_id = os.path.basename(root)
        for file in files:
            # 將檔案名稱加上目錄名稱作為前綴，並用底線連接
            # 例如：0006.jpg -> 66b23c0ba92d600001883983_0006.jpg
            try:
                old_path = os.path.join(root, file)
                # 檢查檔案是否已經有產品ID前綴，避免重複操作
                if not file.startswith(f"{product_id}_"):
                    new_file_name = f"{product_id}_{file}"
                    new_path = os.path.join(root, new_file_name)
                    os.rename(old_path, new_path)
                    print(f"Renamed: {old_path} -> {new_path}")
                else:
                    print(f"Skipping: {file} already has product ID prefix.")
            except Exception as e:
                print(f"Error renaming {file} in {root}: {e}")

if __name__ == "__main__":
    rename_images()
