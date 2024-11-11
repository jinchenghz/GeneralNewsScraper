import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from lxml import etree
from GeneralNewsScraper.BrowserContextAsync import BrowserContext
from GeneralNewsScraper.parse_article import parse_article_title, parse_article_content, parse_time, \
    pre_process_article, parse_top_image, parse_site_name, parse_domain, parse_logo
from GeneralNewsScraper.parse_article_list import parse_article_list


class GNS:
    def __init__(self):
        # self.browserContext = BrowserContext()
        self.pagination_count = 0
        self.article_list = []
        self.article_url_list = []

    async def parse_article_list_async(self, url, html=None, pagination=0):
        """
        提取新闻网站列表页的文章url
        :param pagination: 翻页数
        :param url: 网站列表页url
        :param html:
        :return: 文章列表
        """
        browserContext = BrowserContext()
        try:
            if not html:
                if not browserContext.browser:
                    await browserContext.initialize()
                page_html, page_url = await browserContext.download_html(url)
            else:
                page_html = html

            _article_list = parse_article_list(page_html, url)
            for _article in _article_list:
                if _article["url"] not in self.article_url_list:
                    self.article_url_list.append(_article["url"])
                    self.article_list.append(_article)

            # 翻页
            _html = etree.HTML(page_html)
            pagination_regex = [
                "//a[text()='Next']/@href",
                "//a/span[text()='Next']/../../a/@href",
                "//a[text()='下一页']/@href",
                "//a/span[text()='下一页']/../../a/@href",
            ]
            pagination_url = None
            for pagination_regex_item in pagination_regex:
                pagination_url = _html.xpath(pagination_regex_item)
                if pagination_url:
                    break
            if pagination_url and self.pagination_count < pagination:
                pagination_url = pagination_url[0]
                if not pagination_url.startswith("http"):
                    pagination_url = urljoin(url, pagination_url)
                # print("翻页：", pagination_url)
                self.pagination_count += 1
                await self.parse_article_list_async(pagination_url, pagination=pagination)
        finally:
            await browserContext.close()
        print("文章列表：", self.article_list)
        return self.article_list

    async def parse_article_async(self, url, html=None):
        """
        解析文章数据
        :param url: 文章url
        :param html: 文章html
        :return: 文章数据
        """
        browserContext = BrowserContext()
        try:
            if not html:
                if not browserContext.browser:
                    await browserContext.initialize()

                article_html, page_url = await browserContext.download_html(url)
            else:
                article_html, page_url = html, url
            # 文章内容预处理
            article_html = pre_process_article(article_html)

            # 获取文章发布时间
            pub_time = parse_time(article_html)

            # 获取文章标题
            title = parse_article_title(article_html)

            # 获取文章内容
            page_content = parse_article_content(article_html, page_url)

            # 获取文章主图片
            top_image = parse_top_image(article_html)

            # 获取网站名称
            site_name = parse_site_name(article_html)

            # 获取域名
            domain = parse_domain(page_url)

            # 获取网站logo
            logo = parse_logo(page_url, article_html)

            if not page_content["imageList"] and top_image:
                page_content["imageList"] = [top_image]

            item = {
                'url': page_url,
                'title': title,
                'pubTime': pub_time,
                "topImage": top_image,
                'siteName': site_name,
                'domain': domain,
                'logo': logo,
                'text': page_content["content"],
                'imageList': page_content["imageList"],
                'videoList': page_content["videoList"],
            }
        finally:
            await browserContext.close()
        return item

    def run_parse_article(self, url):
        asyncio.run(self.parse_article_async(url))

    async def parse_article_all_async(self, url):
        """
        解析文章数据
        :param url: url
        :return: 文章数据列表
        """
        url_list = [i["url"] for i in await self.parse_article_list_async(url)]
        with ThreadPoolExecutor(max_workers=6) as executor:
            loop = asyncio.get_running_loop()
            tasks = []
            for url in url_list:
                tasks.append(loop.run_in_executor(executor, self.run_parse_article, url))
            await asyncio.gather(*tasks)


def article_list(url, html=None, pagination=0):
    articles = asyncio.run(GNS().parse_article_list_async(url=url, html=html, pagination=pagination))
    return articles


def article(url, html=None):
    article_info = asyncio.run(GNS().parse_article_async(url=url, html=html))
    return article_info


def article_parse_all(url):
    article_info_list = asyncio.run(GNS().parse_article_all_async(url))
    return article_info_list
