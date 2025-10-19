import json
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def get_taobao_page_content(url, cookies_json_str):
    """
    Fetches the full HTML content of a Taobao shop page using Playwright.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in headed mode for debugging
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Load cookies if provided
        if cookies_json_str:
            try:
                cookies = json.loads(cookies_json_str)
                await context.add_cookies(cookies)
            except json.JSONDecodeError:
                print("Warning: Could not parse cookies JSON string.")


        page = await context.new_page()

        # Evade detection
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            print("Page loaded. Waiting for content...")

            # Wait for a selector that indicates the shop content is loaded
            await page.wait_for_selector(".shop-hesper-bd", timeout=30000)
            print("Shop content detected. Scrolling to load all items...")

            # Scroll down to ensure all dynamic content is loaded
            last_height = await page.evaluate("document.body.scrollHeight")
            for _ in range(5): # Scroll a few times
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000) # Wait for content to load
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            print("Scrolling complete. Fetching page content.")
            html_content = await page.content()
            return html_content

        except Exception as e:
            print(f"An error occurred during scraping: {e}")
            html_content = await page.content()
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Page source on error saved to error_page.html")
            return None
        finally:
            print("Closing browser.")
            await browser.close()

async def main():
    # It's recommended to be logged in to Taobao in a regular browser,
    # then use a cookie editor extension to export your cookies as a JSON string.
    # Paste the JSON string here. Without valid cookies, Taobao might block the request or show a login page.
    cookies_json_str = r'''
    [{"name":"thw","value":"tw","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":false,"sameSite":"Lax"},{"name":"cookie2","value":"11fe95e33b5acf29cc0f6e66d76138ec","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"t","value":"f4cbac1e18168ce9ab2ef3f900560d69","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_tb_token_","value":"337eaf3aeb3f7","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_samesite_flag_","value":"true","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"_m_h5_tk","value":"35850f98e89c626417563f5a428fa5f0_1760756557137","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_m_h5_tk_enc","value":"e26a69fce67d92ee39db4971e75efad7","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"hng","value":"TW%7Czh-TW%7CTWD%7C158","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"mt","value":"ci=0_0","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"3PcFlag","value":"1760746938035","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cna","value":"0tl3IVHOcC8CAQGgBISCPkNJ","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"unb","value":"3574652060","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"sn","value":"","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"uc3","value":"vt3=F8dD2ky%2FIf3L%2FE8FjtQ%3D&id2=UNX8jvTVGb%2BL7g%3D%3D&lg2=UtASsssmOIJ0bQ%3D%3D&nk2=EF8fUbBhLqpO","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"csg","value":"d15782e3","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"lgc","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cancelledSubSites","value":"empty","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cookie17","value":"UNX8jvTVGb%2BL7g%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"dnk","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"skt","value":"ba41e494985cd856","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"existShop","value":"MTc2MDc0Njk0Nw%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"uc4","value":"nk4=0%40EoZgD0Pxz2V3Qc41OtCir45x078%3D&id4=0%40UgJ5PaC4oE2o8Mxj%2Fi5AFAYLyuiV","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"tracknick","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_cc_","value":"URm48syIZQ%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_l_g_","value":"Ug%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"sg","value":"u08","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"_nk_","value":"santosliu","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"cookie1","value":"UNN8H3FUVo4OpBUe0loHdh5QdXott4gptN9u%2BzsS5Ro%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"wk_cookie2","value":"16cc879962ebea852bf7417787e7a965","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"wk_unb","value":"UNX8jvTVGb%2BL7g%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"sgcookie","value":"E100zFHoKB3XVSZ44hCaNsxrhZPOm%2Feo5x0hwdgkkJ8ViigTvIdWD4GL%2F%2FmKFOKOsFUWjGsGhI0O8Z7fxe2fl%2FiFo5uEGQKP2z3U42w2RrvKgMc%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":true,"secure":true,"sameSite":"None"},{"name":"_hvn_lgc_","value":"0","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"uc1","value":"cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&cookie21=U%2BGCWk%2F7oPIg&cookie14=UoYY4%2FxVg0jGeg%3D%3D&pas=0&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"},{"name":"isg","value":"BBcXO824M5xosLcQhL35nk9HpothXOu-KZIcMWlEM-ZNmDfacSx7DtWq-DCGcMM2","domain":".taobao.com","path":"/","expires":-1,"httpOnly":false,"secure":true,"sameSite":"None"}]
    '''

    target_url = "https://h5api.m.taobao.com/h5/mtop.taobao.shop.simple.item.fetch/1.0/?jsv=2.6.2&appKey=12574478&t=1760782837860&sign=b62473d1435417ec0e6380608377fd66&api=mtop.taobao.shop.simple.item.fetch&type=originaljson&v=1.0&timeout=10000&dataType=json&sessionOption=AutoLoginAndManualLogin&needLogin=true&LoginRequest=true&jsonpIncPrefix=_1760782837860_&data=%7B%22page%22%3A1%2C%22orderType%22%3A%22first_new%22%2C%22sortType%22%3A%22%22%2C%22catId%22%3A0%2C%22keyword%22%3A%22%22%2C%22filterType%22%3A%22%22%2C%22shopId%22%3A%2235283664%22%2C%22sellerId%22%3A%2272458074%22%7D"

    html_content = await get_taobao_page_content(target_url, cookies_json_str)

    if html_content:
        # Save the content to a file to verify
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("\nFull page content saved to output.html")
        # You can also parse it with BeautifulSoup here if needed
        # soup = BeautifulSoup(html_content, 'html.parser')
        # print(soup.prettify())

if __name__ == '__main__':
    asyncio.run(main())
