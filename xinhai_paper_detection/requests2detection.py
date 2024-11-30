import re
import requests
from urllib.parse import quote
from tqdm import tqdm
from bs4 import BeautifulSoup
from opencc import OpenCC
import time
import random

# 配置文件路径定义
CONFIG_PATH = './config'
ARTICLE_PATH = './article.txt'
OUTPUT_HTML = './plagiarism_results.html'

# 初始化繁简转换器
cc = OpenCC('t2s')  # 将繁体转换为简体


def read_config(file_path):
    """
    从config中读取配置

    :param file_path: config文件路径
    :return: config，字典
    """
    config = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            if ',' in value:
                config[key] = value.split(',')
            else:
                config[key] = int(value) if value.isdigit() else value
    return config


def read_article(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def search_google(query, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"):
    """
        对输入的文本段进行搜索

        :param query: 查询词，即待查的文本段
        :return: 搜索结果中各项的摘要
        """
    query = quote(query)
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": user_agent
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    search_results = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')
    return [result.text for result in search_results]


def check_plagiarism(text_fragments, length_threshold=30, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)", delay=2):
    """
    主函数

    :param text_fragments: 分割后的文本列表
    :param length_threshold: 文本长度阈值，跳过低于阈值的文本
    :return: 结果，含文本段和搜索页链接
    """
    plagiarism_results = []
    for fragment in tqdm(text_fragments, desc="Checking Plagiarism Progress"):
        if not fragment.strip() or len(fragment) < length_threshold:
            continue

        search_results = search_google(fragment, user_agent)

        # 随机延时
        time.sleep(random.uniform(0, delay))

        simple_fragment = cc.convert(fragment)

        for result in search_results:
            simple_result = cc.convert(result)
            match_count = calculate_match_count(simple_fragment, simple_result)

            if match_count > length_threshold:
                plagiarism_results.append({
                    'fragment': fragment,
                    'url': f"https://www.google.com/search?q={quote(fragment)}"
                })
                print(f"Fragment: {fragment}")
                print(f"Result: {result}")
                print(f"URL: https://www.google.com/search?q={quote(fragment)}\n")
                break

    return plagiarism_results


def calculate_match_count(fragment, result):
    """计算两个字符串中连续匹配的字符数"""
    max_match = 0
    current_match = 0
    fragment_len = len(fragment)
    result_len = len(result)

    for i in range(fragment_len):
        for j in range(result_len):
            k = 0
            while (i + k < fragment_len and j + k < result_len
                   and fragment[i + k] == result[j + k]):
                k += 1
            if k > max_match:
                max_match = k

    return max_match


def write_results_to_html(results, file_path):
    html_content = """
    <html>
    <head>
        <title>Plagiarism Check Results</title>
    </head>
    <body>
        <h1>Plagiarism Check Results</h1>
        <ul>
    """
    for result in results:
        html_content += f"""
        <li>
            <p>Fragment: {result['fragment']}</p>
            <p>URL: <a href="{result['url']}" target="_blank">{result['url']}</a></p>
        </li>
        <hr>
        """
    html_content += """
        </ul>
    </body>
    </html>
    """

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)


def split_text(input_text, delimiters=None, max_length=2000, unwanted_symbols=None):
    """
    将输入文本分割为若干片段，同时去除不需要的干扰符号。

    :param input_text: 要分割的文本
    :param delimiters: 分隔符列表，默认为中文句号、问号、感叹号、省略号
    :param max_length: Google搜索允许的最大字符数，用于再次分割长片段
    :param unwanted_symbols: 需要去除的干扰符号列表
    :return: 分割后的片段列表
    """
    unwanted_pattern = '[' + re.escape(''.join(unwanted_symbols)) + ']'
    cleaned_text = re.sub(unwanted_pattern, '', input_text)
    delimiter_pattern = '|'.join(map(re.escape, delimiters))
    sentences = re.split(delimiter_pattern, cleaned_text)

    final_fragments = []
    for sentence in sentences:
        sentence = sentence.strip()
        while len(sentence) > max_length:
            split_point = sentence.rfind(' ', 0, max_length)
            if split_point == -1:
                split_point = max_length

            final_fragments.append(sentence[:split_point].strip())
            sentence = sentence[split_point:].strip()

        if sentence:
            final_fragments.append(sentence)

    return final_fragments


# 读取配置
config = read_config(CONFIG_PATH)

# 文章文本读取
article = read_article(ARTICLE_PATH)

fragments = split_text(article,
                       unwanted_symbols=config.get('unwanted_symbols'),
                       delimiters=config.get('delimiters'),
                       max_length=config.get('max_length'))

plagiarism_results = check_plagiarism(fragments,
                                      length_threshold=config.get('length_threshold'),
                                      user_agent=config.get('user_agent'),
                                      delay=config.get('delay'))  # 设置匹配字数阈值

# 写入 HTML 文件
write_results_to_html(plagiarism_results, OUTPUT_HTML)