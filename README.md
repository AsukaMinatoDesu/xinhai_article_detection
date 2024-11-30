chromedriver下载，版本号修改为本地Chrome对应版本，32位/64位都行，向下兼容：
https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.100/win32/chromedriver-win32.zip

待优化：
1. selenium处理效率低（以添加requests选项）
2. 文本分割的分隔符需要手动设置
3. 文本长度阈值需要手动设置
4. 对于以关键词形式重复出现的搜索结果过滤不足

2024年11月29日17:22:51更新：
1. 默认文本读取方式更改为文件读取，文件路径 './article.txt'
2. 将参数配置转移到config文件中，文件路径 './config'，参数如下： 
   unwanted_symbols：引号等需要去除的干扰符号
   delimiters：分隔符号
   max_length：分隔后的文本长度最大值
   threshold_length：阈值长度，忽略短于阈值的文本段，忽略短于阈值的搜索结果
3. 隐藏浏览器窗口
4. 以n/m的形式输出当前进度

2024年11月30日13:55:20更新（requests2detection.exe相关）：
1. 新增requests2detection，使用requests模块编写，无需驱动且速度更快，但匹配效果有所下降，且太长的文本可能会被服务器发现
2. 新增参数user_agent
3. 新增参数delay，get申请随机延时，延时范围[0, delay]，单位：秒
4. 优化进度显示功能，实时显示已匹配到的结果
