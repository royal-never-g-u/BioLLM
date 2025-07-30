import jieba

# 示例句子
sentence = "我爱自然语言处理技术，尤其是关键词提取功能"

# 使用jieba进行分词
words = jieba.lcut(sentence)

# 简单关键词提取（实际项目中可以增加停用词过滤、词性筛选等逻辑）
keywords = [word for word in words if len(word) > 1]

print("提取的关键词：", keywords)
