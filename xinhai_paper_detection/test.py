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

print("请输入文章（输入end input结束）：")
lines = []
while True:
    line = input()
    if line == "end input":
        break
    lines.append(line)

article = "\n".join(lines)
fragments = split_text(article,
                       unwanted_symbols=['“', '”', '「', '」', '『', '』', '"', "'", '‘', '’', '\n'],
                       delimiters=['。', '？', '！'])

print("\n分割后的片段：")
for fragment in fragments:
    print(fragment)