import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
from tqdm import tqdm

# 配置文件路径定义
CONFIG_PATH = './config'
ARTICLE_PATH = './article.txt'
OUTPUT_HTML = './plagiarism_results.html'

def read_config(file_path):
    # 从配置文件中读取参数
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
    # 从文本文件中读取文章
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def search_google(driver, query):
    """
    对输入的文本段进行搜索

    :param driver: 浏览器驱动
    :param query: 查询词，即待查的文本段
    :return: 搜索结果中各项的匹配文字长度列表
    """
    # 编码查询词
    query = quote(query)
    # 使用Google进行搜索
    url = f"https://www.google.com/search?q={query}"
    driver.get(url)

    # 确保页面加载完毕
    time.sleep(2)

    # 查找所有<div class="MjjYud">元素（搜索结果）
    big_sections = driver.find_elements(By.XPATH, '//div[@class="MjjYud"]')
    results = []

    for section in big_sections:
        # 在每一个大类下找所有高亮文本<em class="t55VCb">（匹配结果）
        highlighted_elements = section.find_elements(By.XPATH, './/em[@class="t55VCb"]')
        total_highlighted_length = sum(len(elem.text) for elem in highlighted_elements)

        results.append(total_highlighted_length)

    return results


def check_plagiarism(text_fragments, threshold_length = 30):
    """
    主函数

    :param text_fragments: 分割后的文本列表
    :param threshold_length: 文本长度阈值，跳过低于阈值的文本
    :return: None
    """
    plagiarism_results = []
    for fragment in tqdm(text_fragments, desc="Checking Plagiarism Progress"):
        # print(f"Progress: {index}/{total_fragments}")
        # 去除首尾空格，检测非空
        if not fragment.strip():
            continue

        # 低于阈值时忽略，缩短用时
        if len(fragment) < threshold_length:
            continue

        search_results = search_google(driver, fragment)

        # 比较总高亮文本长度与原文本长度
        for total_highlighted_length in search_results:
            if total_highlighted_length > threshold_length:
                plagiarism_results.append({
                    'fragment': fragment,
                    'url': f"https://www.google.com/search?q={quote(fragment)}"
                })
                # print(f"Fragment: {fragment}")
                # print(f"URL: https://www.google.com/search?q={quote(fragment)}\n")
                break

    return plagiarism_results

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

    # 去除不需要的干扰符号
    unwanted_pattern = '[' + re.escape(''.join(unwanted_symbols)) + ']'
    cleaned_text = re.sub(unwanted_pattern, '', input_text)

    # 将用户提供的标点符号列表转为正则表达式中的字符类
    delimiter_pattern = '|'.join(map(re.escape, delimiters))

    # 首次按标点符号进行初步分割
    sentences = re.split(delimiter_pattern, cleaned_text)

    # 处理过长的句子，将其按最大长度再次分割
    final_fragments = []
    for sentence in sentences:
        sentence = sentence.strip()
        # 如果句子大于max_length，则进一步分割
        while len(sentence) > max_length:
            # 找一个合适的分割点（max_length之内的最后一个空格）
            split_point = sentence.rfind(' ', 0, max_length)
            # 如果找不到合适的空格，那就在max_length强行截断
            if split_point == -1:
                split_point = max_length

            final_fragments.append(sentence[:split_point].strip())
            sentence = sentence[split_point:].strip()

        # 把最后剩余的部分添加进去
        if sentence:
            final_fragments.append(sentence)

    return final_fragments

# 读取配置
config = read_config(CONFIG_PATH)

# 文章文本读取
article = read_article(ARTICLE_PATH)


# 设置Chrome选项
options = Options()
options.add_argument("--headless")  # 无头模式
# 创建Chrome WebDriver
driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=options)


# 输入区读取
# print("输入文章（输入endinput结束）：")
# lines = []
# while True:
#     line = input()
#     if line == "endinput":
#         break
#     lines.append(line)
#
# article = "\n".join(lines)

fragments = split_text(article,
                       unwanted_symbols=config.get('unwanted_symbols'),
                       delimiters=config.get('delimiters'),
                       max_length=config.get('max_length'))

plagiarism_results = check_plagiarism(fragments, threshold_length=config.get('threshold_length'))

# 写入 HTML 文件
write_results_to_html(plagiarism_results, OUTPUT_HTML)

driver.quit()
