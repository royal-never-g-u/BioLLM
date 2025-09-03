# 系统命令和Agent优先级分析

## 概述

BioLLM系统采用多层次的优先级机制来处理用户输入，确保最合适的命令或agent被执行。系统按照以下优先级顺序处理用户输入：

## 优先级层次结构

### 🥇 第一优先级：特殊命令（Special Commands）
**优先级：最高**
**触发条件：** 用户输入包含特定关键词或虚拟命令匹配

#### 1.1 下载命令（Download）
- **关键词匹配**：`download`, `get`, `fetch`, `obtain`, `retrieve`
- **处理逻辑**：
  ```python
  # 检查用户输入是否包含下载关键词
  download_virtual_keywords = ['download', 'get', 'fetch', 'obtain', 'retrieve']
  if any(keyword in user_input_lower for keyword in download_virtual_keywords):
      # 提取模型名称
      # 执行下载操作
  ```
- **执行方法**：`download_model()`
- **功能**：下载生物仿真模型文件

#### 1.2 分析命令（Analyse）
- **关键词匹配**：`analyze`, `analyse`, `analysis`, `examine`, `study`, `investigate`
- **处理逻辑**：
  ```python
  # 检查用户输入是否包含分析关键词
  analyse_virtual_keywords = ['analyze', 'analyse', 'analysis', 'examine', 'study', 'investigate']
  if any(keyword in user_input_lower for keyword in analyse_virtual_keywords):
      # 提取模型名称
      # 检查模型文件是否存在
      # 执行分析操作
  ```
- **执行方法**：`model_analyzer.run()`
- **功能**：分析COBRA模型

### 🥈 第二优先级：虚拟命令（Virtual Commands）
**优先级：高**
**触发条件**：虚拟命令agent识别到用户意图

#### 2.1 虚拟命令识别
- **执行方法**：`virtual_command_agent.match_command(user_input)`
- **置信度阈值**：`confidence >= 0.1`
- **支持的虚拟命令**：
  - `choose_model`：选择生物仿真模型
  - `analyse_model`：分析模型

#### 2.2 模型选择命令
```python
if command_name == 'choose_model':
    # 获取可用模型列表
    available_models = rag_tool.get_saved_biosimulation_models()
    # 提取模型名称
    found_model = extract_model_name(user_input, available_models)
    # 尝试下载对应模型文件
    download_result = download_tool.download_model_from_name(found_model)
```

#### 2.3 模型分析命令
```python
elif command_name == 'analyse_model':
    # 跳过，让后续的回退机制处理
    pass
```

### 🥉 第三优先级：分析命令匹配
**优先级：中**
**触发条件**：模型分析器识别到分析意图

#### 3.1 分析命令处理
- **执行方法**：`model_analyzer.match_command(user_input)`
- **置信度阈值**：`confidence >= 0.1`
- **处理逻辑**：
  ```python
  if command_name == 'analyse':
      model_name = analyse_match.get('model_name')
      if model_name:
          # 检查模型文件是否存在
          model_file = f"../downloads/{model_name}.mat"
          if os.path.exists(model_file):
              result = model_analyzer.run(f"analyse {model_name}")
          else:
              result = f"❌ Model file '{model_name}.mat' not found..."
      else:
          # 显示可用模型
          result = model_analyzer.run("analyse")
  ```

### 🏅 第三点五优先级：Agent for Agent
**优先级：中低**
**触发条件**：用户输入不包含常规命令前缀

#### 3.5.1 Agent for Agent处理
- **执行方法**：`agent_for_agent.check_biological_relevance(user_input)`
- **置信度阈值**：`confidence >= 0.7`
- **处理逻辑**：
  ```python
  # 首先检查是否已包含常规命令
  contains_regular_command = False
  for cmd in regular_commands.keys():
      if cmd_lower.startswith(cmd):
          contains_regular_command = True
          break
  
  # 如果没有常规命令，检查生物研究相关性
  if not contains_regular_command:
      agent_result = agent_for_agent.check_biological_relevance(user_input)
      if agent_result['is_relevant']:
          # 自动添加knowledge命令
          user_input = agent_result['modified_input']
  ```
- **功能**：智能判断用户输入是否与生物研究相关，如果相关则自动添加knowledge命令

### 🏅 第四优先级：常规命令（Regular Commands）
**优先级：低**
**触发条件**：用户输入以特定命令开头

#### 4.1 常规命令列表
```python
regular_commands = {
    "generate": code_writer.run,           # 代码生成
    "explain": code_explainer.run,         # 代码解释
    "debug": code_debugger.run,            # 代码调试
    "execute": code_executor.run,          # 代码执行
    "knowledge": rag_tool.run,             # 知识库查询
    "literature": literature_agent.run,    # 文献搜索
    "literature_query": literature_query,  # 文献查询
    "list_literature_kbs": list_literature_kbs,  # 列出文献知识库
    "search": search_and_answer,           # 搜索和回答
    "update_data": lambda: rag_tool.update_knowledge_base(),  # 更新数据
    "force_update": lambda: rag_tool.force_update_knowledge_base(),  # 强制更新
    "models": show_models                  # 显示模型
}
```

#### 4.2 命令匹配逻辑
```python
cmd_lower = user_input.lower().strip()
matched_cmd = None
for cmd in regular_commands.keys():
    if cmd_lower.startswith(cmd):
        matched_cmd = cmd
        break

if matched_cmd:
    if matched_cmd in ["update_data", "force_update"]:  # 无提示命令
        result = regular_commands[matched_cmd]()
    else:  # 有提示的命令
        prompt = strip_command(user_input, matched_cmd)
        result = regular_commands[matched_cmd](prompt)
```

### 🎯 第五优先级：默认聊天（Default Chat）
**优先级：最低**
**触发条件**：所有其他优先级都未匹配

#### 5.1 默认处理
```python
if not matched:
    result = code_writer.chat(user_input, memory)
```

## 详细处理流程

### 步骤1：特殊命令检查
1. **检查下载关键词**：如果用户输入包含下载相关词汇
2. **提取模型名称**：从输入中识别具体的模型名称
3. **执行下载**：调用下载工具下载模型文件
4. **检查分析关键词**：如果用户输入包含分析相关词汇
5. **验证模型文件**：检查模型文件是否存在
6. **执行分析**：调用模型分析器进行分析

### 步骤2：虚拟命令处理
1. **虚拟命令识别**：使用虚拟命令agent识别用户意图
2. **置信度检查**：确保置信度达到阈值（≥0.1）
3. **命令分发**：
   - `choose_model`：处理模型选择
   - `analyse_model`：跳过，让后续机制处理
   - 其他命令：返回未实现消息

### 步骤3：分析命令匹配
1. **分析意图识别**：使用模型分析器识别分析意图
2. **置信度检查**：确保置信度达到阈值（≥0.1）
3. **模型验证**：检查指定的模型文件是否存在
4. **执行分析**：调用模型分析器执行分析

### 步骤3.5：Agent for Agent处理
1. **常规命令检查**：检查用户输入是否已包含常规命令前缀
2. **生物相关性判断**：如果无常规命令，使用LLM判断是否与生物研究相关
3. **置信度评估**：确保置信度达到阈值（≥0.7）
4. **输入修改**：如果相关，自动在输入前添加knowledge命令

### 步骤4：常规命令匹配
1. **命令前缀检查**：检查用户输入是否以已知命令开头
2. **命令分类**：
   - **无提示命令**：`update_data`, `force_update`
   - **有提示命令**：其他所有命令
3. **参数提取**：使用`strip_command()`提取命令参数
4. **命令执行**：调用对应的agent或工具

### 步骤5：默认聊天
1. **回退处理**：如果所有命令都未匹配
2. **通用聊天**：使用代码编写器进行通用对话

## 优先级决策树

```
用户输入
    ↓
检查特殊命令关键词
    ↓
是 → 执行特殊命令
    ↓
否 → 检查虚拟命令
    ↓
是 → 执行虚拟命令
    ↓
否 → 检查分析命令
    ↓
是 → 执行分析命令
    ↓
否 → 检查是否包含常规命令
    ↓
是 → 跳过Agent for Agent
    ↓
否 → Agent for Agent检查生物相关性
    ↓
相关 → 添加knowledge命令
    ↓
不相关 → 继续处理
    ↓
检查常规命令
    ↓
是 → 执行常规命令
    ↓
否 → 默认聊天
```

## 关键特性

### 1. 置信度阈值
- **虚拟命令**：`confidence >= 0.1`
- **分析命令**：`confidence >= 0.1`
- **目的**：避免误触发，确保命令识别的准确性

### 2. 回退机制
- **逐级回退**：从高优先级到低优先级依次尝试
- **容错处理**：即使某个优先级失败，也会尝试下一个
- **最终保障**：默认聊天确保用户总能得到响应

### 3. 命令提取
- **前缀匹配**：使用`startswith()`进行命令前缀匹配
- **参数分离**：使用`strip_command()`分离命令和参数
- **大小写不敏感**：统一转换为小写进行比较

### 4. 状态管理
- **匹配标志**：使用`matched`标志控制流程
- **执行标志**：使用`special_command_executed`标志避免重复执行
- **内存管理**：使用`memory`对象保存对话历史

## 优化建议

### 1. 优先级调整
- 可以根据使用频率调整优先级顺序
- 可以添加用户偏好设置

### 2. 置信度优化
- 可以动态调整置信度阈值
- 可以添加机器学习模型提高识别准确性

### 3. 命令扩展
- 可以添加更多虚拟命令类型
- 可以支持命令别名和缩写

### 4. 性能优化
- 可以添加命令缓存机制
- 可以实现并行命令识别

## 总结

BioLLM系统采用六层优先级机制，确保用户输入得到最合适的处理：

1. **特殊命令**：处理下载和分析等核心功能
2. **虚拟命令**：处理自然语言意图识别
3. **分析命令**：处理模型分析相关请求
4. **Agent for Agent**：智能判断生物研究相关性并自动添加knowledge命令
5. **常规命令**：处理标准命令格式
6. **默认聊天**：提供通用对话支持

这种设计既保证了核心功能的优先级，又提供了灵活的自然语言交互能力，同时确保了系统的健壮性和用户体验。
