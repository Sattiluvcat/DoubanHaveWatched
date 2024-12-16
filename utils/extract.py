import re

import pycountry
from translate import Translator


def translate_to_english(name):
    name = name.replace('·', '')
    try:
        return Translator(from_lang="Chinese", to_lang="English").translate(name)
    except RuntimeError:
        return name


def is_country(name):
    name = translate_to_english(name)
    # print("翻译后", name)
    if name == 'UK' or name == 'Mainland China' or name == 'Taiwan, China' or name == 'Macao, China':
        return True
    try:
        country = pycountry.countries.lookup(name)
        return True
    except LookupError:
        return False


def extract_first_date(info):
    # 使用正则表达式匹配第一个日期，不包括括号部分
    match = re.search(r'\d{4}-\d{2}-\d{2}', info)
    if match:
        return match.group(0)
    return None


def actor_actress(info, num):
    # 特殊情况：2021-05-28(美国/美国网络) / 2021-06-06(中国大陆) / 艾玛·斯通
    parts = info.split('/')
    names = []
    for part in parts:
        if not re.search(r'\d{4}-\d{2}-\d{2}', part):
            # 正则表达式匹配的是中文名
            names.extend(re.findall(r'[\u4e00-\u9fa5·]+(?:\s[\u4e00-\u9fa5·]+)*', part))
        if len(names) >= num:
            break
    return names[:num]


# 有的电视剧格式比较奇怪 比如没有导演只有编剧 此处不再进行详细处理（主要还是看电影吧
# 以及某些短片
def director_duration_tags(info, tag_list):
    duration_match = re.search(r'\d+ ?分钟', info)
    # 选择第一个时长
    duration = None
    director = None
    tags = []
    if duration_match:
        duration = duration_match.group(0)
        # 匹配导演-->最后一个中文名
        text_before_duration = info[:duration_match.start()]
        # 以斜杠为标志，分割导演
        director_match = re.findall(r'[\u4e00-\u9fa5·]+(?:\s[\u4e00-\u9fa5·]+)*', text_before_duration)
        # print(director_match)
        if director_match:
            for name in reversed(director_match):
                # print(name)
                if '·' in name:
                    director = name
                    continue
                if (name == '中国香港' or name == '中国大陆' or name == '中国澳门' or name == '中国台湾' or name == '美国'
                        or name == '苏联' or is_country(name)):
                    # print(name)
                    break
                director = name
        # 匹配标签
        text_after_duration = info[duration_match.end():]
        slash_index = text_after_duration.find('/')
        if slash_index != -1:
            # print(text_after_duration)
            # 检查时长之后的所有信息 如果有标签则提取
            for tag in text_after_duration.split('/'):
                tag = tag.strip()
                # print("tag:",tag)
                if tag in tag_list:
                    tags.append(tag)
    # 返回方式后面可更改
    return director, duration, tags


# 匹配语言-->从末尾扫描
def language(info):
    # 颠倒顺序
    reverse_info = info[::-1]
    # 匹配语言
    languages = []
    parts = reverse_info.split('/')
    for part in parts:
        language_match = re.search(r'(语[\u4e00-\u9fa5]+|话[\u4e00-\u9fa5]+|言方[\u4e00-\u9fa5]+)', part)
        if language_match:
            # 颠倒回来
            languages.append(language_match.group(0)[::-1])
        else:
            break
    languages.reverse()
    return languages
