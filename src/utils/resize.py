"""
縮小過大的圖片
超過 1024kb 就縮
要縮到 1024kb

"""

import os
from PIL import Image


products_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'products')

print(products_dir)

for root, dirs, files in os.walk(products_dir):
    for file in files:
        file_path = os.path.join(root, file)
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:
            print(f'路徑：{file_path}，檔案大小：{file_size}')

            # 使用 Pillow 縮小圖片至 1024KB
            try:
                img = Image.open(file_path)
                # 檢查圖片模式，如果是 RGBA 則轉換為 RGB，因為 JPEG 不支援透明度
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                quality = 90 # 初始品質
                while True:
                    # 暫存到記憶體中，以便檢查檔案大小
                    # 注意：這裡直接保存會覆蓋原檔案，如果需要保留原檔案，應保存到臨時檔案
                    img.save(file_path, optimize=True, quality=quality)
                    new_file_size = os.path.getsize(file_path)
                    
                    if new_file_size <= 1024 * 1024:
                        print(f'圖片已縮小至 {new_file_size} bytes')
                        break
                    
                    quality -= 5 # 每次降低品質 5
                    if quality < 10: # 防止品質過低
                        print(f'警告：無法將圖片縮小至 1024KB 以下，目前大小：{new_file_size} bytes')
                        break
            except Exception as e:
                print(f'處理圖片 {file_path} 時發生錯誤: {e}')
