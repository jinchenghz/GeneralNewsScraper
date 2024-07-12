from GeneralNewsScraper import GNS

# 解析文章列表页
page_html = """ html示例 """
articles = GNS.article_list(url="https://www.voachinese.com/", html=page_html)
print(articles)

# 解析文章详情页
article_html = """ html示例 """
article_info = GNS.article(url="https://www.voachinese.com/a/exiled-chinese-businessman-guo-s-trial-nears-close/7693596.html", html=article_html)
print(article_info)
