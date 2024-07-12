from urllib.parse import urlparse
from spellchecker import SpellChecker


def is_valid_url(url):
    """
    判断给定的字符串是否为一个有效的URL。
    :param url: 要检查的字符串
    :return: 如果是有效的URL则返回True，否则返回False
    """
    try:
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme) and bool(parsed_url.netloc)
    except ValueError:
        return False


def spell_check(words: list):
    """
    检查单词拼写是否正确，返回错误的单词
    :param words:
    :return:
    """
    result_list = []
    for word in words:
        if not word.isalpha():
            result_list.append(word)
        elif len(word) >= 20:
            result_list.append(word)
    spell = SpellChecker(language='en')
    misspelled = spell.unknown(words)
    return list(misspelled) + result_list
