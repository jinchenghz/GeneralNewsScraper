import asyncio
from loguru import logger
from GeneralNewsScraper.BrowserContextAsync import BrowserContext
from GeneralNewsScraper.parse_article import parse_article_title, parse_article_content, parse_time, \
    pre_process_article, parse_top_image, parse_site_name, parse_domain, parse_logo
from GeneralNewsScraper.parse_article_list import parse_article_list


class GNS:
    def __init__(self):
        self.browserContext = BrowserContext()

    async def parse_article_list_async(self, url=None, html=None):
        """
        提取新闻网站列表页的文章url
        :param url: 网站列表页url
        :param html:
        :return: 文章列表
        """
        if not (url or html):
            logger.error("url以及html参数不能同时为空")
        if not html:
            if not self.browserContext.browser:
                await self.browserContext.initialize()
            page_html = await self.browserContext.download_html(url)
        else:
            page_html = html
        article_list = parse_article_list(page_html, url)
        return article_list

    async def parse_article_async(self, url, html=None):
        """
        解析文章数据
        :param url: 文章url
        :param html: 文章html
        :return: 文章数据
        """
        if not html:
            if not self.browserContext.browser:
                await self.browserContext.initialize()

            article_html = await self.browserContext.download_html(url)
        else:
            article_html = html
        # 文章内容预处理
        article_html = pre_process_article(article_html)

        # 获取文章发布时间
        pub_time = parse_time(article_html)

        # 获取文章标题
        title = parse_article_title(article_html)

        # 获取文章内容
        page_content = parse_article_content(article_html, url)

        # 获取文章主图片
        top_image = parse_top_image(article_html)

        # 获取网站名称
        site_name = parse_site_name(article_html)

        # 获取域名
        domain = parse_domain(url)

        # 获取网站logo
        logo = parse_logo(url, article_html)

        if top_image and top_image not in page_content["imageList"]:
            page_content["imageList"] = [top_image] + page_content["imageList"]

        item = {
            'url': url,
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
        return item


def article_list(url=None, html=None):
    articles = asyncio.run(GNS().parse_article_list_async(url=url, html=html))
    return articles


def article(url, html=None):
    article_info = asyncio.run(GNS().parse_article_async(url=url, html=html))
    return article_info
