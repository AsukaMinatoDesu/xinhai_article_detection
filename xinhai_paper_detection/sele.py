import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote

# 设置Chrome选项
options = Options()
options.headless = True  # 无头模式
# 创建Chrome WebDriver
driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=options)

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

    for fragment in text_fragments:
        # 去除首尾空格，检测非空
        if not fragment.strip():
            continue

        # 低于阈值时忽略，缩短用时
        if len(fragment) < threshold_length:
            continue

        results = search_google(driver, fragment)

        # 比较总高亮文本长度与原文本长度
        for total_highlighted_length in results:
            if total_highlighted_length > threshold_length:
                print(f"Fragment: {fragment}")
                print(f"URL: https://www.google.com/search?q={quote(fragment)}\n")
                break

    return 0


def split_text(input_text, delimiters=None, max_length=2000, unwanted_symbols=None):
    """
    将输入文本分割为若干片段，同时去除不需要的干扰符号。

    :param input_text: 要分割的文本
    :param delimiters: 分隔符列表，默认为中文句号、问号、感叹号、省略号
    :param max_length: Google搜索允许的最大字符数，用于再次分割长片段
    :param unwanted_symbols: 需要去除的干扰符号列表
    :return: 分割后的片段列表
    """
    import re

    # 默认不需要的干扰符号
    if unwanted_symbols is None:
        unwanted_symbols = ['“', '”', '「', '」', '『', '』', '"', "'", '‘', '’', '\n']

    # 去除不需要的干扰符号
    unwanted_pattern = '[' + re.escape(''.join(unwanted_symbols)) + ']'
    cleaned_text = re.sub(unwanted_pattern, '', input_text)

    # 如果没有传入自定义的分隔符，则使用默认的中文标点符号
    if delimiters is None:
        delimiters = ['。', '？', '！', '……']

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

print("输入文章（输入endinput结束）：")
lines = []
while True:
    line = input()
    if line == "endinput":
        break
    lines.append(line)

article = "\n".join(lines)
fragments = split_text(article,
                       unwanted_symbols=['“', '”', '「', '」', '『', '』', '"', "'", '‘', '’', '\n'],
                       delimiters=['。', '？', '！'],
                       max_length=64)

plagiarism_results = check_plagiarism(fragments, threshold_length=20)


driver.quit()
