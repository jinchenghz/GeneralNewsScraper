import os


class BrowserContext:
    """
    浏览器上下文
    """

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        from playwright.async_api import async_playwright
        current_dir_path = os.path.abspath(os.path.dirname(__file__))
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        with open(f'{current_dir_path}/stealth.min.js', 'r') as f:
            js_code = f.read()
        await self.page.add_init_script(js_code)

    async def download_html(self, url):
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
        except Exception as e:
            print(f"Failed to load URL, trying again: {e}")
            try:
                await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            except Exception as e:
                print(f"Failed to load URL after retry: {e}")
                raise e
        return await self.page.content()

    async def request_get(self, url):
        response = await self.page.request.get(url)
        content = await response.body()
        return content.decode()

    async def close(self):
        if self.browser:
            await self.browser.close()
