import json
import time
import asyncio
import os
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .utils.db import setTaobaoProduct, checkTaobaoProductID, setTaobaoOption

async def get_item_page(item_data, cookies_json_str):
    """
    Fetches a single Taobao item page using Playwright and saves its content.
    """
    item_id = item_data.get("itemId")
    url = item_data.get("itemUrl")
    print(f"--- [get_item_page] 開始執行，商品 ID: {item_id} ---")
    async with async_playwright() as p:
        print("[get_item_page] 啟動 Playwright")
        browser = await p.chromium.launch(headless=False)  # Run in headed mode
        print("[get_item_page] 啟動瀏覽器")
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        print("[get_item_page] 建立新的瀏覽器上下文")

        # Load cookies
        print("[get_item_page] 正在載入 cookies")
        cookies = json.loads(cookies_json_str)
        await context.add_cookies(cookies)
        print("[get_item_page] Cookies 載入成功")

        page = await context.new_page()
        print("[get_item_page] 開啟新分頁")

        # Evade detection
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("[get_item_page] 注入反偵測腳本")

        try:
            print(f"[get_item_page] 準備前往 URL: {url}")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            print(f"[get_item_page] 成功載入頁面: {url}")
            
            # A simple wait to ensure dynamic content has a chance to load
            print("[get_item_page] 等待 5 秒以載入動態內容")
            await page.wait_for_timeout(5000)
            html_content = await page.content()
            print("[get_item_page] 成功獲取頁面內容")

            # Ensure the output directory exists
            output_dir = 'output'
            if not os.path.exists(output_dir):
                print(f"[get_item_page] 建立 output 資料夾: {output_dir}")
                os.makedirs(output_dir)

            # Save the content to a file
            file_path = os.path.join(output_dir, "item_page.html")
            print(f"[get_item_page] 準備將內容儲存至: {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"[get_item_page] 成功儲存頁面內容至 {file_path}")
            
            return "item_page.html"

        except Exception as e:
            print(f"[get_item_page] 爬取過程中發生錯誤 {url}: {e}")
            html_content = await page.content()
            error_file_path = os.path.join('output', "item_page.html")
            print(f"[get_item_page] 準備將錯誤時的頁面源碼儲存至: {error_file_path}")
            with open(error_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"[get_item_page] 錯誤頁面源碼已儲存至 {error_file_path}")
            return "item_page.html"
        finally:
            print("[get_item_page] 關閉瀏覽器")
            await browser.close()
            print(f"--- [get_item_page] 執行完畢，商品 ID: {item_id} ---")

async def get_option_data(item_data,data):
    skuBase = data.get('loaderData', {}).get('home', {}).get('data', {}).get('res', {}).get('skuBase', {})
    skuCore = data.get('loaderData', {}).get('home', {}).get('data', {}).get('res', {}).get('skuCore', {})
    product_presale = 0
    options_to_insert = []
               
    if skuBase and 'skus' in skuBase and 'props' in skuBase:
        props_map = {prop['pid']: prop for prop in skuBase.get('props', [])}
        
        for sku in skuBase.get('skus', []):
            option_data = {}
            option_data['option_id'] = sku.get('skuId')
            propPath = sku.get('propPath')
            if propPath:
                names = []
                for pair in propPath.split(';'):
                    if ':' in pair:
                        pid, vid = pair.split(':', 1)
                        if pid in props_map and vid in props_map[pid].get('valueMap', {}):
                            name = props_map[pid]['valueMap'][vid].get('name')
                            if name:
                                name = name.replace('，仅售展示盒', '')
                                name = re.sub(r'[（\(][^）\)]*[）\)]', '', name).strip()
                                if name.startswith('+'):
                                    name = name[1:]
                                names.append(name)
                
                if names:
                    option_text = '+'.join(names)
                    price = 0
                    if skuCore and 'sku2info' in skuCore:
                        sku_id = option_data.get('option_id')
                        if sku_id and sku_id in skuCore['sku2info']:
                            price_money = skuCore['sku2info'][sku_id].get('price', {}).get('priceMoney')
                            if price_money:
                                try:
                                    price = int(int(price_money) / 100) * 11
                                except (ValueError, TypeError):
                                    print(f"Could not parse price_money: {price_money}")
                                
                    print(f"SKU ID: {option_data['option_id']}, Option Name: {option_text}, Option Price:{price}")
                    
                    option_to_db = (
                        item_data.get("itemId"),
                        option_data.get('option_id'),
                        item_data.get("itemUrl"),
                        item_data.get("title"),
                        '', # summary
                        price,
                        option_text,
                        '' # detail
                    )

                    if '预售' in option_text:
                        product_presale = 1
                    else:
                        options_to_insert.append(option_to_db)
                        product_presale = 0
        
        if options_to_insert:
            setTaobaoOption(options_to_insert)

    return product_presale

                    
async def parse_result_html(item_data, html_file):
    print(f"--- [parse_result_html] 開始執行，檔案: {html_file} ---")
    if not html_file:
        print("[parse_result_html] 錯誤: 未提供 HTML 檔案。")
        return "HTML file not provided."
    
    file_path = os.path.join('output', html_file)
    print(f"[parse_result_html] 準備讀取檔案: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print("[parse_result_html] 檔案讀取成功")
        soup = BeautifulSoup(content, "html.parser")
        scripts = soup.find_all("script")
        print(f"[parse_result_html] 找到 {len(scripts)} 個 script 標籤")
        if len(scripts) >= 40:
            print("[parse_result_html] 找到第 40 個 script 標籤，準備解析")
            script_tag_str = str(scripts[39])
            
            prefix = '<script>!(function () {var a = window.__ICE_APP_CONTEXT__ || {};var b = '
            suffix = ';for (var k in a) {b[k] = a[k]}window.__ICE_APP_CONTEXT__=b;})();</script>'
            
            if script_tag_str.startswith(prefix) and script_tag_str.endswith(suffix):
                print("[parse_result_html] 前後綴匹配成功，準備提取 JSON")
                json_str = script_tag_str[len(prefix):-len(suffix)]
                
                try:
                    data = json.loads(json_str)
                    print("[parse_result_html] JSON 解析成功")
                    product_data = {}
                    

                    images = data.get('loaderData', {}).get('home', {}).get('data', {}).get('res', {}).get('item', {}).get('images')
                    if images is not None:
                        print("[parse_result_html] 成功提取圖片列表")
                        product_data['image_list'] = images
                        print(f"--- [parse_result_html] 執行完畢，檔案: {html_file} ---")
                    else:
                        print("[parse_result_html] 錯誤: 在指定路徑下找不到 'images' 資料")
                        return "Could not find 'images' data at the specified path."

                    product_data['product_presale'] = await get_option_data(item_data,data)

                except json.JSONDecodeError as e:
                    print(f"[parse_result_html] 錯誤: JSON 解碼失敗: {e}")
                    return f"Failed to decode JSON after stripping prefix/suffix: {e}"

                return product_data
            else:
                print("[parse_result_html] 錯誤: 第 40 個 script 標籤的前後綴不匹配")
                return "Prefix or suffix not found in the 40th script tag."
        else:
            print(f"[parse_result_html] 錯誤: 找不到第 40 個 script 標籤")
            return f"Could not find the 40th script. Only found {len(scripts)} scripts."
    except FileNotFoundError:
        print(f"[parse_result_html] 錯誤: 找不到檔案 {file_path}")
        return f"Error: File not found at {file_path}"
    except Exception as e:
        print(f"[parse_result_html] 讀取或解析檔案時發生未知錯誤 {file_path}: {e}")
        return f"An error occurred while reading {file_path}: {e}"

async def main():
    print("--- [main] 開始執行 ---")
    cookies_json_str = r'''
    [{"name":"thw","value":"tw","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":false,"sameSite":"Lax"},{"name":"cookie2","value":"11fe95e33b5acf29cc0f6e66d76138ec","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"t","value":"f4cbac1e18168ce9ab2ef3f900560d69","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_tb_token_","value":"337eaf3aeb3f7","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_samesite_flag_","value":"true","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"_m_h5_tk","value":"35850f98e89c626417563f5a428fa5f0_1760756557137","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_m_h5_tk_enc","value":"e26a69fce67d92ee39db4971e75efad7","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"hng","value":"TW%7Czh-TW%7CTWD%7C158","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"mt","value":"ci=0_0","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"3PcFlag","value":"1760746938035","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cna","value":"0tl3IVHOcC8CAQGgBISCPkNJ","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"unb","value":"3574652060","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"sn","value":"","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"uc3","value":"vt3=F8dD2ky%2FIf3L%2FE8FjtQ%3D&id2=UNX8jvTVGb%2BL7g%3D%3D&lg2=UtASsssmOIJ0bQ%3D%3D&nk2=EF8fUbBhLqpO","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"csg","value":"d15782e3","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"lgc","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cancelledSubSites","value":"empty","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cookie17","value":"UNX8jvTVGb%2BL7g%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"dnk","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"skt","value":"ba41e494985cd856","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"existShop","value":"MTc2MDc0Njk0Nw%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"uc4","value":"nk4=0%40EoZgD0Pxz2V3Qc41OtCir45x078%3D&id4=0%40UgJ5PaC4oE2o8Mxj%2Fi5AFAYLyuiV","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"tracknick","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_cc_","value":"URm48syIZQ%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_l_g_","value":"Ug%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"sg","value":"u08","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_nk_","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cookie1","value":"UNN8H3FUVo4OpBUe0loHdh5QdXott4gptN9u%2BzsS5Ro%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"wk_cookie2","value":"16cc879962ebea852bf7417787e7a965","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"wk_unb","value":"UNX8jvTVGb%2BL7g%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"sgcookie","value":"E100zFHoKB3XVSZ44hCaNsxrhZPOm%2Feo5x0hwdgkkJ8ViigTvIdWD4GL%2F%2FmKFOKOsFUWjGsGhIO8Z7fxe2fl%2FiFo5uEGQKP2z3U42w2RrvKgMc%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"_hvn_lgc_","value":"0","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"uc1","value":"cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&cookie21=U%2BGCWk%2F7oPIg&cookie14=UoYY4%2FxVg0jGeg%3D%3D&pas=0&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"isg","value":"BBcXO824M5xosLcQhL35nk9HpothXOu-KZIcMWlEM-ZNmDfacSx7DtWq-DCGcMM2","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"}]
    '''
    
    # Load items from taobao.json
    print("[main] 準備從 taobao.json 載入商品列表")
    try:
        with open("taobao.json", "r", encoding="utf-8") as f:
            taobao_data = json.load(f)
        items = taobao_data.get("data", {}).get("data", [])
        print(f"[main] 成功從 taobao.json 載入 {len(items)} 個商品")
    except FileNotFoundError:
        print("[main] 錯誤: 找不到 taobao.json 檔案。")
        return
    except json.JSONDecodeError:
        print("[main] 錯誤: 無法解碼 taobao.json。")
        return

    if not items:
        print("[main] taobao.json 中沒有找到任何商品。")
        return

    products_to_insert = []
    # Process each item
    print("[main] 開始處理商品列表")
    for i, item in enumerate(items):
        print(f"\n[main] --- 正在處理第 {i+1}/{len(items)} 個商品 ---")
        item_data = {
            "itemId": item.get("itemId"),
            "itemUrl": item.get("itemUrl"),
            "title": item.get("title")
        }
        item_id = item_data.get("itemId")
        item_url = item_data.get("itemUrl")
        item_title = item_data.get("title")
        item_feature = item.get("image")
        
        if item_id and item_url:
            print(f"[main] 商品 ID: {item_id}, 標題: {item_title}")
            # Ensure URL has a scheme
            if item_url.startswith('//'):
                item_url = 'https:' + item_url
                item_data['itemUrl'] = item_url
                print(f"[main] URL 已修正為: {item_url}")
            elif not item_url.startswith(('http://', 'https://')):
                 item_url = 'https:' + item_url
                 item_data['itemUrl'] = item_url
                 print(f"[main] URL 已修正為: {item_url}")
            
            print("[main] 正在檢查資料庫中是否已存在該商品")
            if checkTaobaoProductID(item_id):
                print(f"[main] 商品 {item_id} 已存在於資料庫中，跳過。")
                continue
            print(f"[main] 商品 {item_id} 不在資料庫中，繼續處理。")

            result_html_file = await get_item_page(item_data, cookies_json_str)
            product_data = await parse_result_html(item_data, result_html_file)
            
            image_list = product_data.get('image_list') if isinstance(product_data, dict) else None
            product_presale = product_data.get('product_presale', 0) if isinstance(product_data, dict) else 0
            image_list_json = json.dumps(image_list) if image_list else None
            
            if image_list_json:
                print(f"[main] 成功解析到商品 {item_id} 的圖片列表")
            else:
                print(f"[main] 警告: 未能解析到商品 {item_id} 的圖片列表。解析結果: {product_data}")
                continue

            products_to_insert.append((item_id, product_presale, item_url, item_title, item_feature, image_list_json))
            print(f"[main] 商品 {item_id} 已加入待寫入資料庫列表")
            
            if products_to_insert:
                print(f"\n[main] 準備將 {len(products_to_insert)} 個新商品寫入資料庫")
                setTaobaoProduct(products_to_insert)
                print("[main] 商品資料寫入資料庫成功")
            else:
                print("[main] 沒有新的商品需要寫入資料庫")
            # Add a delay between requests to be polite
            print("[main] 等待 60 秒後處理下一個商品")
            await asyncio.sleep(60)
        else:
            print(f"[main] 警告: 第 {i+1} 個商品缺少 itemId 或 itemUrl，跳過。")

    
    
    print("--- [main] 執行完畢 ---")

if __name__ == '__main__':
    asyncio.run(main())
