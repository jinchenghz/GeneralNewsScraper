# 单位距离
import re

from lxml import etree


def get_longest_node(html, node_name):
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
        if 'cookies' in node:
            continue
        count = len(node.strip())
        if count > max_count:
            max_count = count
            max_node_text = node
    return max_node_text



def get_tree_distance(node1, node2):
    # 获取从节点到根的路径
    def get_path_to_root(node):
        path = []
        while node:
            path.append(node)
            node = node.parent
        return path

    path1 = get_path_to_root(node1)
    path2 = get_path_to_root(node2)

    # 反转路径，使其从根节点开始
    path1.reverse()
    path2.reverse()

    # 找到第一个不同的节点
    i = 0
    while i < len(path1) and i < len(path2) and path1[i] == path2[i]:
        i += 1

    # 计算距离
    return (len(path1) - i) + (len(path2) - i)

def aaa(html):
    if isinstance(html, str):
        html_str = re.sub(r'<script[^>]*?>.*?</script>', '', html, flags=re.S)
        html_str = re.sub(r'<style[^>]*?>.*?</style>', '', html_str, flags=re.S)
        html_str = re.sub(r'<path[^>]*?>.*?</path>', '', html_str, flags=re.S)
        html = etree.HTML(html_str)
    max_p_text = get_longest_node(html, 'p')
    max_div_text = get_longest_node(html, 'div')
    target_node = 'p' if len(max_p_text) > len(max_div_text) else 'div'
    max_node_text = max_p_text if len(max_p_text) > len(max_div_text) else max_div_text
    node_list = html.xpath('//*')
    paragraph_count_list = []
    for node in node_list:
        paragraph_count_list.append(len(node.xpath(f'./{target_node}')))
    max_count = max(paragraph_count_list)

    # 获取标题的node
    title_node = html.xpath('//title')
    if not title_node:
        title_node = html.xpath('//h1')
    title_node = title_node[0] if title_node else None
    for node in node_list:
        tree_distance = get_tree_distance(title_node, node) - 1
        print("距离: ", tree_distance)

        for _count in range(max_count, 0, -1):
            if len(node.xpath(f'./{target_node}')) == _count and max_node_text in node.xpath('.//*/text()'):
                content = '\n'.join(i.strip() for i in node.xpath('.//*/text()'))
                content = re.sub(r'[\n]+', '\n', content).strip()


def get_score(html):
    node_list = []
    html = etree.HTML(html)
    node_list.extend(html.xpath('//p|//div'))


