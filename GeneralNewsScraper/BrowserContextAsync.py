import os
from playwright.async_api import async_playwright
import aiofiles

current_dir_path = os.path.abspath(os.path.dirname(__file__))


class BrowserContext:
    """
    浏览器上下文
    """

    # def __init__(self):
    #   self.browser = None
    #   self.context = None
    #   self.page = None
    #   self.playwright = None

    async def download_html(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            async with aiofiles.open(f'{current_dir_path}/stealth.min.js', 'r') as f:
                js_code = await f.read()
                await page.add_init_script(js_code)
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                return await page.content(), page.url
            except Exception as e:
                print(f"Failed to load URL, trying again with domcontentloaded mode: {e}")
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    return await page.content(), page.url
                except Exception as e:
                    print(f"Failed to load URL after retry: {e}")
                    raise e
