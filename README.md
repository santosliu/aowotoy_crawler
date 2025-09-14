# toybox-crawler

- 爬取指定網頁
  - https://shop35283664.world.taobao.com/?spm=pc_detail.29232929.shop_block.dshopinfo.6a747dd6BFC0gG
  - (done) https://www.aowotoys.com/categories/aowobox-displaybox?sort_by=created_at&order_by=desc&limit=72&page= 
- 存入資料庫
- 輸出指定 csv 格式
  - (done) ruten
  - shopee
  - jolly
- 輸出到指定網站

# 待處理

中文字網址 https://www.aowotoys.com/products/aowobox-%E9%AB%98%E9%80%8F%E6%89%8B%E8%BE%A6%E4%B8%BB%E9%A1%8C%E5%B1%95%E7%A4%BA%E7%9B%92-%E9%81%A9%E7%94%A8%E6%96%BC-%E6%93%8E%E8%92%BC%E5%B7%A5%E4%BD%9C%E5%AE%A4-%E6%B4%9B%E5%A4%A9%E4%BE%9D-%E6%A2%A8%E8%8A%B1%E9%9B%AAver%E6%89%8B%E8%BE%A6?locale=zh-hant

No data fetched for product_id 66c4420fd2f6d7001f6b1c9b



20250813 start from optionId 16204 productId 9387
20250902 start from optionID 17246 productId 10435
--

## 手動處理

- 每兩周作一次

- 定期檢查新商品
  - python src/aowotoy_latest.py 
- 執行 resize.py 處理圖片大小
  - python src/utils/resize.py
- 處理完之後 rename
  - python src/utils/rename.py
- 定期 rclone sync 到 cloudflare 上
  - 開啟終端處理
  - 切換到 aowotoy_crawler 目錄之後
  - D:\Dropbox\01_工具程式\rclone-v1.69.3-windows-amd64\rclone sync products r2:toy --progress -v
- 輸出成 Shopee + Jolly 用 CSV
  - 輸出前記得調整輸出範圍 by product_id
  - python -m src.export.jolly
  - python -m src.export.shopee
- shopee + jolly 確認完成後再處理 ruten
- 上傳到 Ruten
  - python -m src.ruten.upload_product
  - python -m src.ruten.upload_picture

