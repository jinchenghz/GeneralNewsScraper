import re
from pprint import pprint
from urllib.parse import urljoin, urlparse

from loguru import logger

from GeneralNewsScraper.utils import spell_check


def parse_id(url):
    """
    解析文章链接id，返回id长度
    :param url:
    :return: id长度
    """
    parsed_url = urlparse(url)
    url_path = parsed_url.path.split('/')[-1]
    str_list = re.findall('\w+', url_path)
    digit_list = []
    for _str in str_list:
        if _str.isdigit():
            digit_list.append(_str)
    id_list = spell_check(str_list)
    id_list.extend(digit_list)
    if not id_list:
        return 0
    return len(max(id_list, key=len))


def verify_obvious_article_url(url):
    """
    判断给定的URL是否为文章链接
    :param url:
    :return:
    """
    tags = ['/a/', '/article/', '/articles/', '/read/']
    for tag in tags:
        if tag in url:
            return True
    part_list = re.split('/', url)
    for part in part_list:
        if len(part.split('-')) >= 4:
            return True


def parse_article_list(page_html, url):
    """
    解析文章列表西文章url以及文章标题
    :param page_html:
    :param url:
    :return:
    """
    page_html = re.sub(r'<!--.*?-->', '', page_html)
    page_html = re.sub(r'\s+', ' ', page_html)
    a_list = [list(a) for a in re.findall(r'<a[^>]*?href="([^"]+?)"[^>]*?>\s*(.*?)\s*</a>', page_html)]
    _a_list = []
    if not a_list:
        return []
    for a in a_list:
        a[1] = re.sub(r'<[^>]+>', " ", a[1]).strip()
        a[1] = re.sub(r'\s+', " ", a[1]).strip()
        if (a[0].endswith("com") or a[0].endswith("cn") or a[0].endswith("net") or a[0].endswith("com/")
                or a[0].endswith("cn/") or a[0].endswith("com/") or a[0].endswith("net/") or 'javascript' in a[0]
                or '.jpg' in a[0] or '.mp4' in a[0] or '.index' in a[0] or len(a[1]) <= 4):
            continue
        _a_list.append([a[0], a[1]])
    # 找到确切的文章的url
    result_list = []
    id_length_dict = dict()
    for a in _a_list:
        if verify_obvious_article_url(a[0]):
            if not a[0].startswith('http'):
                a[0] = urljoin(url, a[0])
            result_list.append({"title": a[1], "url": a[0]})

        id_length = parse_id(a[0])
        # print(id_length)
        if id_length in id_length_dict.keys():
            id_length_dict[id_length] += 1
        else:
            id_length_dict[id_length] = 1

    max_id_length = max([{'length': x, 'times': y} for x, y in id_length_dict.items()], key=lambda x: x['times'])
    if max_id_length['length'] > 3:
        for a in _a_list:
            if parse_id(a[0]) == max_id_length['length'] and a[0] not in [x['url'] for x in result_list]:
                # print('a', a)
                a[1] = re.sub(r'<[^>]+>', "", a[1]).strip()
                if not a[0].startswith('http'):
                    a[0] = urljoin(url, a[0])
                result_list.append({"title": a[1], "url": a[0]})
    # logger.info(result_list)
    return result_list
