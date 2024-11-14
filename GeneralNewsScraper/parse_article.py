import datetime
import re
from urllib.parse import urljoin, urlparse
from lxml import etree
from GeneralNewsScraper.utils import is_valid_url


async def pre_process_article(page_html):
    """
    文章内容预处理
    :param article_html:
    :return:
    """
    regex_patterns = [
        # r'<script[^>]*?>.*?</script>',
        r'<style[^>]*?>.*?</style>',
        r'<!--.*?-->',
        r'Notice: The content above \(including the pictures and videos if any\) is uploaded and posted by a user of NetEase Hao, which is a social media platform and only provides information storage services.',
    ]
    for regex in regex_patterns:
        page_html = re.sub(regex, '', page_html, flags=re.S)
    return page_html


async def parse_time(html):
    """
    html 中提取时间
    :param html:
    :return: 字符串类型时间
    """
    regex_patterns = [
        '"(20[012]\d-[01]\d-[0-3]\d[ T]+[012]\d:[0-5]\d:[0-5]\d)',
        '"(20[012]\d-[01]\d-[0-3]\d[ T]+[012]\d:[0-5]\d)',
        '(20[012]\d-[01]\d-[0-3]\d[ T]+[012]\d:[0-5]\d:[0-5]\d)',
        '(20[012]\d-[01]\d-[0-3]\d[ T]+[012]\d:[0-5]\d)',
        '(20[012]\d-[01]\d-[0-3]\d)',
    ]
    for regex in regex_patterns:
        match = re.findall(regex, html)
        if match:
            for m in match:
                pub_time = m.strip()
                pub_time = pub_time.replace('T', ' ')
                if not re.search('\d{2}:\d{2}:\d{2}', pub_time):
                    if not re.search('\d{2}:\d{2}', pub_time):
                        pub_time = pub_time + ' 00:00:00'
                    elif re.search('\d{2}:\d{2}', pub_time):
                        pub_time = pub_time + ':00'
                if datetime.datetime.strptime(pub_time,
                                              '%Y-%m-%d %H:%M:%S').timestamp() > datetime.datetime.now().timestamp():
                    continue
                return pub_time


async def get_longest_node(html, node_name):
    """
    获取最长文本的node标签
    :param html:
    :param node_name:
    :return:
    """
    node_list = html.xpath(f'//{node_name}/text()')
    max_count = 0
    max_node_text = ''
    for node in node_list:
        # 增加异常判断条件
        if 'cookies' in node or 'copyright' in node or 'Copyright' in node or 'All rights reserved' in node:
            # print(node)
            continue
        count = len(node.strip())
        if count > max_count:
            max_count = count
            max_node_text = node
    return max_node_text


async def parse_article_title(article_html):
    """
    获取文章标题
    :param article_html:
    :return:
    """
    patterns = [
        '<meta property="[^"]*?title" content="([^"]+?)">',
        '<title[^>]*?>\s*(.+?)\s*</title>',
        '<h1[^>]*?>(.+?)<',
    ]

    for pattern in patterns:
        match = re.search(pattern, article_html)
        if match:
            title = match.group(1).strip()
            break
    else:
        raise Exception("未匹配到标题")
    title = re.sub(r'<[^>]+>', '', title)
    # title = title.split('-')[0].strip()
    # title = title.split('_')[0].strip()
    # title = title.split('|')[0].strip()
    return title


async def parse_article_content(html, url):
    """
    获取文章内容
    思路：
    1.找到文章中最长的段落
    2.判断这个段落是p标签内的文本还是div标签内的文本
    3.在html中查找内容段落的上一层node节点
    :param html:
    :param url:
    :return:
    """
    if isinstance(html, str):
        html_str = re.sub(r'<script[^>]*?>.*?</script>', '', html, flags=re.S)
        html_str = re.sub(r'<style[^>]*?>.*?</style>', '', html_str, flags=re.S)
        html_str = re.sub(r'<path[^>]*?>.*?</path>', '', html_str, flags=re.S)
        html = etree.HTML(html_str)
    max_p_text = await get_longest_node(html, 'p')
    max_div_text = await get_longest_node(html, 'div')
    target_node = 'p' if len(max_p_text) > len(max_div_text) else 'div'
    max_node_text = max_p_text if len(max_p_text) > len(max_div_text) else max_div_text
    node_list = html.xpath('//*')
    paragraph_count_list = []
    for node in node_list:
        paragraph_count_list.append(len(node.xpath(f'./{target_node}')))
    max_count = max(paragraph_count_list)

    content = ''
    img_list = []
    video_list = []
    for node in node_list:
        for _count in range(max_count, 0, -1):
            if len(node.xpath(f'./{target_node}')) == _count and max_node_text in node.xpath('.//*/text()'):
                content = '\n'.join(i.strip() for i in node.xpath('.//*/text()'))
                content = re.sub(r'[\n]+', '\n', content).strip()

                img_list = []
                video_list = []

                _img_list = node.xpath('.//img/@src')
                for img in _img_list:
                    if ('.log' in img or '.ico' in img or '.gif' in img or 'data:image' in img or '.svg' in img or
                            'base64' in img or ' ' in img):
                        continue
                    if img in img_list or img == url:
                        continue
                    if not img.startswith('http'):
                        img = urljoin(url, img)
                    if await is_valid_url(img):
                        img_list.append(img)

                _video_list = node.xpath('.//video/@src')
                for video in _video_list:
                    if not ('.mp4' in video) or ' ' in video:
                        continue
                    if video in video_list:
                        continue
                    if not video.startswith('http'):
                        video = urljoin(url, video)
                    if await is_valid_url(video):
                        video_list.append(video)
                break

    return {"content": content, "imageList": img_list, "videoList": video_list}


async def parse_top_image(html):
    image = re.findall('<meta[^>]*?content="([^"]*?)"[^>]*?property="[^"]*?image"', html)
    if not image:
        image = re.findall('<meta[^>]*?property="[^"]*?image"[^>]*?content="([^"]*?)"', html)
    return image[0] if image else None


async def parse_site_name(html):
    """
    获取网站名称
    :param html:
    :return:
    """
    ret = re.findall('property="og:site_name" content="([^"]*?)"', html)
    if ret:
        return ret[0]
    # if not ret:
    #     ret = re.findall('<title[^>]*?>[^_\-|<]*?[_\-|](.+?)</title>', html)
    #     if not ret:
    #         return None
    # webName = ret[0]
    # if '-' in ret[0]:
    #     webName = webName.split('-')[-1]
    # if '|' in ret[0]:
    #     webName = webName.split('|')[-1]
    # if '_' in ret[0]:
    #     webName = webName.split('_')[-1]
    #
    # return webName.strip()


async def parse_logo(url, html):
    """
    获取网站icon
    :param url:
    :param html:
    :return:
    """
    patterns = [
        '"([^"]*?.ico)"',
        '<[^>]*?="[^"]*?icon"[^>]*? href="([^"]*?)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            icon_url = match.group(1)
            return icon_url if icon_url.startswith("http") else urljoin(url, icon_url)
    # 获取url域名
    _url = urlparse(url)
    _hostname = _url.hostname
    _scheme = _url.scheme
    if not _hostname:
        return None
    if not _scheme:
        _scheme = "https"
    return _scheme + '://' + _url.hostname + '/favicon.ico'


async def parse_domain(url):
    """
    获取域名
    :param url:
    :return:
    """
    return urlparse(url).hostname
