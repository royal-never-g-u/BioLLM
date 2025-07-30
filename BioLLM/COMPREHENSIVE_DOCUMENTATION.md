# BioLLM 综合文档

## 项目概述

BioLLM是一个基于LangChain和Qwen-Plus API的多功能AI代码助手，支持Python/Matlab代码生成、解释、调试、执行、联网搜索、RAG知识增强和记忆功能，CLI交互。特别针对生物仿真模型分析进行了优化。

## 主要功能

### 核心功能
- 代码生成、解释、调试、执行（Python/Matlab）
- 通用对话问答
- 联网搜索
- RAG（本地知识库增强）
- 记忆功能

### 生物仿真模型功能
- **模型检测与交互** - 自动检测LLM回答中的生物仿真模型名称，提供可点击按钮
- **模型下载** - 从BIGG数据库下载COBRA模型文件
- **模型分析** - 分析COBRA模型并提供详细的可视化报告
- **可视化功能** - 生成图表和HTML报告展示模型结构

---

## 1. 生物仿真模型按钮功能

### 功能概述

当LLM的回答中包含`BiosimulationModels.txt`中记载的有效模型名称时，系统会自动：

1. **检测模型名称** - 在LLM回答中识别生物仿真模型名称
2. **创建可点击按钮** - 为检测到的模型创建蓝色下划线样式的按钮
3. **触发模型选择** - 点击按钮后自动输入"I want to use [model_name] for the experiment"进入agent系统

### 支持的模型
- Recon1, Recon2, Recon3D
- e_coli_core, core E. coli metabolic model
- iMM904, iND750, iAF1260, iJD668, iJO1366, iML1515, iRC1083
- human erythrocyte metabolic network

### 技术实现

#### 模型检测算法
```python
def detect_models_in_text(text, models):
    detected_models = []
    for model in models:
        pattern = re.compile(re.escape(model), re.IGNORECASE)
        matches = pattern.finditer(text)
        for match in matches:
            detected_models.append({
                'model': model,
                'start': match.start(),
                'end': match.end(),
                'original_text': text[match.start():match.end()]
            })
    return detected_models
```

#### 按钮显示逻辑
```python
def display_text_with_model_buttons(text, detected_models):
    st.markdown(text)  # 显示原始文本
    
    if detected_models:
        st.markdown("**Available models in this response:**")
        cols = st.columns(min(len(detected_models), 3))
        
        for i, detection in enumerate(detected_models):
            col_idx = i % len(cols)
            with cols[col_idx]:
                unique_key = f"model_btn_{detection['model']}_{int(time.time() * 1000)}_{i}_{hash(text)}"
                
                if st.button(f"📊 {detection['model']}", key=unique_key):
                    st.session_state.model_selection = f"I want to use {detection['model']} for the experiment"
                    st.rerun()
```

### 工作流程

1. **模型检测阶段**
   ```
   LLM回答: "The iMM904 model is excellent for metabolic analysis"
   ↓
   系统检测: 在BiosimulationModels.txt中查找"iMM904"
   ↓
   检测结果: 找到匹配的模型名称
   ```

2. **按钮显示阶段**
   ```
   检测到模型: iMM904
   ↓
   创建按钮: 📊 iMM904 (蓝色下划线样式)
   ↓
   显示位置: 在LLM回答下方显示"Available models in this response:"
   ```

3. **用户交互阶段**
   ```
   用户点击: 📊 iMM904 按钮
   ↓
   系统模拟输入: "I want to use iMM904 for the experiment"
   ↓
   触发虚拟命令: choose_model (置信度: 1.00)
   ```

4. **命令执行阶段**
   ```
   虚拟命令匹配: choose_model
   ↓
   模型名称提取: iMM904
   ↓
   下载逻辑执行: 调用download_tool.download_model_from_name("iMM904")
   ↓
   文件下载: 下载iMM904.mat文件到downloads目录
   ```

---

## 2. 命令分组与回退机制

### 命令分组

#### 📦 特殊命令 (优先级1)
这些命令具有虚拟命令识别功能，可以从自然语言输入中识别生物仿真模型：

##### Download Command
- **关键词**: `download`, `get`, `fetch`, `obtain`, `retrieve`
- **功能**: 从BIGG数据库下载生物仿真模型
- **示例**:
  ```
  "download e_coli_core"
  "I want to download the iMM904 model"
  "Can you fetch the iND750 model"
  "Please get the Recon1 model"
  "Retrieve the e_coli_core metabolic model"
  ```

##### Analyse Command
- **关键词**: `analyze`, `analyse`, `analysis`, `examine`, `study`, `investigate`
- **功能**: 分析COBRA模型并提供详细信息
- **示例**:
  ```
  "analyse e_coli_core"
  "Please analyze the iMM904 model"
  "Study the iND750 metabolic model"
  "Examine the Recon1 model"
  "Investigate the e_coli_core reactions"
  ```

#### 🛠️ 常规命令 (优先级2)
当特殊命令不匹配或失败时执行：

- `generate`: 生成代码
- `explain`: 解释代码或概念
- `debug`: 调试代码
- `execute`: 执行代码
- `knowledge`: 访问知识库
- `search`: 搜索信息
- `update_data`: 更新知识库
- `force_update`: 强制更新知识库
- `models`: 显示可用模型

### 回退机制

#### 处理流程
```
用户输入
    ↓
步骤1: 检查特殊命令
    ↓
[下载/分析虚拟命令检测]
    ↓
[模型名称提取]
    ↓
[执行特殊命令]
    ↓
[成功?] → 是 → 返回结果
    ↓ 否
步骤2: 检查虚拟命令
    ↓
[虚拟命令检测]
    ↓
[执行虚拟命令]
    ↓
[成功?] → 是 → 返回结果
    ↓ 否
步骤3: 检查分析命令
    ↓
[分析命令检测]
    ↓
[执行分析命令]
    ↓
[成功?] → 是 → 返回结果
    ↓ 否
步骤4: 回退到常规命令
    ↓
[常规命令检测]
    ↓
[执行常规命令]
    ↓
[成功?] → 是 → 返回结果
    ↓ 否
步骤5: 最终回退到默认聊天
    ↓
[默认聊天响应]
```

#### 错误处理

##### 特殊命令错误
当特殊命令失败时：
1. **模型未找到**: 系统提供可用模型列表
2. **下载失败**: 系统显示错误消息并建议重试
3. **分析失败**: 系统建议先下载模型
4. **文件未找到**: 系统建议下载模型

##### 回退行为
- 如果特殊命令不匹配用户输入 → 回退到常规命令
- 如果特殊命令失败 → 回退到常规命令
- 如果没有常规命令匹配 → 回退到默认聊天
- 如果所有命令失败 → 回退到默认聊天

---

## 3. Analyse命令使用指南

### 功能特性

#### 🔬 模型分析
- **基本结构分析**: 分析.mat模型文件的结构
- **COBRA集成**: 使用COBRA框架进行详细的代谢分析
- **结构化数据分析**: 处理代谢模型中的复杂结构化数组
- **数据导出**: 将模型数据导出为CSV文件以供进一步分析

#### 📊 分析组件

##### 代谢物分析
- 代谢物总数
- 按细胞器分类的代谢物（如细胞质、细胞外、线粒体）
- 样本代谢物名称和分子式
- 连接性分析（每个代谢物参与的反应数量）

##### 反应分析
- 反应总数
- 可逆与不可逆反应
- 反应复杂度（每个反应的代谢物数量）
- 样本反应名称和子系统

##### 基因分析
- 基因总数
- 功能与非功能基因
- 基因-反应关联
- 样本基因名称

##### 网络分析
- 按连接性排序的顶级代谢物
- 按代谢物数量排序的顶级反应
- 化学计量矩阵分析
- 稀疏性分析

### 使用方法

#### 智能命令识别

analyse命令支持智能识别用户输入，类似于系统中的其他代理。它可以检测分析相关关键词并自动从用户输入中提取模型名称。

##### 直接命令
```bash
# 列出可用模型
analyse

# 分析特定模型
analyse e_coli_core
analyze iMM904
analyse iND750
```

##### 自然语言输入
命令可以理解自然语言请求：
- "can you analyse the e_coli_core model?"
- "I want to analyze the iMM904 metabolic model"
- "please analyze the iND750 model for me"

##### 基于关键词的识别
命令识别各种关键词：
- "metabolic analysis of e_coli_core"
- "cobra model analysis for iMM904"
- "metabolic network analysis iND750"
- "analyse model"
- "metabolic analysis"
- "analyze metabolic model"

### 可用模型

系统目前支持分析以下模型：

1. **e_coli_core**: E. coli核心代谢模型
   - 72个代谢物，95个反应，137个基因
   - 2个细胞器：细胞质(c)，细胞外(e)

2. **iMM904**: S. cerevisiae代谢模型
   - 1,226个代谢物，1,577个反应，905个基因
   - 8个细胞器：细胞质、细胞外、线粒体等

3. **iND750**: S. cerevisiae代谢模型
   - 1,059个代谢物，1,266个反应，750个基因
   - 8个细胞器：细胞质、细胞外、线粒体等

### 输出

#### 控制台输出
命令提供详细分析，包括：
- 模型结构摘要
- 代谢物、反应和基因统计
- 细胞器分析
- 顶级连接代谢物和反应
- 网络连接信息

#### 数据导出
命令自动将模型数据导出到`model_data/[model_name]/`目录中的CSV文件：

- `metabolites.csv`: 完整的代谢物信息
- `reactions.csv`: 完整的反应信息
- `genes.csv`: 完整的基因信息
- `structure_info.json`: 模型结构元数据

#### 可视化功能
- 生成11种不同类型的可视化图表
- 创建美观的HTML报告
- 提供数据下载链接

### 示例输出

```
🔬 Model Analysis: e_coli_core
==================================================

📊 Basic Model Structure:
------------------------------
Total data objects: 1
Structured arrays: 1
Matrices: 0
Vectors: 0
Scalars: 0

🧬 Structured Arrays (Metabolic Models):
  - e_coli_core: (1, 1) with fields: mets, metNames, metFormulas, metCharge, genes, rxnGeneMat, grRules, rxns, rxnNames, subSystems, S, lb, ub, b, c, rev, description

🧬 COBRA Model Analysis:
------------------------------
Metabolites: 72
Reactions: 95
Genes: 137

📊 Metabolites Analysis:
  - e: 20 metabolites
  - c: 52 metabolites

⚡ Reactions Analysis:
  - Reversible: 46
  - Irreversible: 49

🧬 Genes Analysis:
  - Functional: 137
  - Non-functional: 0

🔗 Top 10 Metabolites by Connectivity:
  1. h_c: 35 reactions
  2. h2o_c: 18 reactions
  3. h_e: 17 reactions
  4. atp_c: 13 reactions
  5. nad_c: 12 reactions

🔗 Top 10 Reactions by Metabolite Count:
  1. BIOMASS_Ecoli_core_w_GAM: 23 metabolites
  2. PPS: 7 metabolites
  3. GLNS: 7 metabolites
  4. GLNabc: 7 metabolites
  5. GLUDy: 7 metabolites

🧬 Structured Model Analysis:
------------------------------
📊 Metabolites: 72
⚡ Reactions: 95
🧬 Genes: 137
🔗 Stoichiometry matrix: (72, 95)

📁 Data exported to: model_data/e_coli_core/
📄 HTML report generated: model_data/e_coli_core/analysis_report.html
📊 Visualizations generated in: model_data/e_coli_core/visualizations
```

---

## 4. Analyse Model虚拟命令

### 功能概述

`analyse_model`虚拟命令允许用户使用自然语言输入分析生物仿真模型。该命令设计为与现有的`analyse`命令一起工作，并提供触发模型分析的替代方法。

### 特性

#### 🎯 智能识别
- 识别与模型分析相关的各种自然语言短语
- 支持"analyze"和"analyse"两种拼写
- 处理不同的句子结构和上下文

#### 📊 模型分析
- 自动从用户输入中提取模型名称
- 检查下载目录中模型文件的存在性
- 运行全面的COBRA模型分析
- 提供代谢物、反应和基因的详细分析

#### 🔄 集成
- 与现有代理系统无缝协作
- 与`choose_model`虚拟命令兼容
- 与下载系统集成以处理缺失的模型

### 使用示例

#### 基本分析请求
```
"Analyze the e_coli_core model"
"I want to analyze the iMM904 model"
"Please analyze the iND750 model"
"Can you analyze this metabolic model"
```

#### 特定分析类型
```
"Analyze metabolites"
"Analyse reactions"
"Analyze genes"
"Analyze metabolic network"
"Analyze COBRA data"
```

#### 自然语言变体
```
"Show me the model analysis"
"Run model analysis"
"Perform model analysis"
"Conduct model analysis"
"Execute model analysis"
"Model analysis please"
```

### 支持的短语

虚拟命令识别以下类型的短语：

#### 核心分析短语
- "Analyze biosimulation model"
- "Analyse metabolic model"
- "Analyze COBRA model"
- "Model analysis"
- "Metabolic analysis"
- "COBRA analysis"

#### 请求变体
- "Analyze the model"
- "Analyse this model"
- "Can you analyze the model"
- "I want to analyze the model"
- "Please analyze the model"

#### 面向行动的短语
- "Show me the model analysis"
- "Display model analysis"
- "Run model analysis"
- "Perform model analysis"
- "Conduct model analysis"
- "Execute model analysis"

#### 特定组件分析
- "Analyze metabolites"
- "Analyse reactions"
- "Analyze genes"
- "Analyze metabolic network"
- "Analyze metabolic pathway"
- "Analyze metabolic system"

#### 数据分析
- "Analyze model data"
- "Analyse model structure"
- "Analyze model components"
- "Analyze COBRA data"
- "Analyse COBRA structure"
- "Analyze biosimulation data"

### 技术实现

#### 文件结构
```
BioLLM/prompts/VirtualCommands/
├── choose_model.txt
└── analyse_model.txt
```

#### 主系统集成
虚拟命令集成到`main.py`中，具有以下逻辑：

1. **命令检测**: 使用`VirtualCommandAgent`检测`analyse_model`命令
2. **模型提取**: 使用与`choose_model`相同的逻辑从用户输入中提取模型名称
3. **文件验证**: 检查`../downloads/`中是否存在相应的`.mat`文件
4. **分析执行**: 调用`ModelAnalyzerAgent`执行分析
5. **错误处理**: 为缺失的模型提供有用的错误消息

#### 处理流程
```
用户输入 → 虚拟命令检测 → 模型名称提取 → 文件检查 → 分析执行
```

### 错误处理

#### 缺失模型文件
如果未找到模型文件，系统提供：
- 指示缺失文件的清晰错误消息
- 建议使用`download`命令下载模型
- 示例: `download e_coli_core`

#### 未指定模型
如果没有提到特定模型：
- 显示数据库中的可用模型
- 提示用户指定模型名称

#### 数据库问题
如果数据库中没有可用模型：
- 建议运行`update_data`或`force_update`
- 提供数据库初始化的清晰说明

---

## 5. 技术实现细节

### 依赖安装
```bash
pip install -r requirements.txt
```

### 启动
```bash
python main.py
```

### 配置
- 在`.env`中填写Qwen-Plus API Key等信息
- 本地知识库请放入`knowledge_base/`目录

### 文件结构
```
BioLLM/
├── agent/                    # 代理模块
│   ├── base.py              # 基础代理类
│   ├── code_writer.py       # 代码生成代理
│   ├── code_explainer.py    # 代码解释代理
│   ├── code_debugger.py     # 代码调试代理
│   ├── code_executor.py     # 代码执行代理
│   ├── download_tool.py     # 模型下载工具
│   ├── model_analyzer_agent.py # 模型分析代理
│   ├── virtual_command_agent.py # 虚拟命令代理
│   └── ...
├── prompts/                  # 提示词文件
│   ├── VirtualCommands/     # 虚拟命令提示词
│   └── ...
├── model_data/              # 模型分析数据
├── downloads/               # 下载的模型文件
├── knowledge_base/          # 知识库
├── main.py                  # 主程序
├── app.py                   # Streamlit应用
└── requirements.txt         # 依赖列表
```

### 模型文件位置
模型文件位于`downloads/`目录：
- `downloads/e_coli_core.mat`
- `downloads/iMM904.mat`
- `downloads/iND750.mat`

---

## 6. 故障排除

### 常见问题

#### 1. 按钮不显示
- 检查是否为knowledge命令
- 确认BiosimulationModels.txt文件存在
- 验证模型名称是否正确

#### 2. 按钮点击无响应
- 检查浏览器控制台是否有错误
- 确认JavaScript是否启用
- 尝试刷新页面

#### 3. 输入框未填充
- 检查网络连接
- 查看控制台日志
- 使用备用方案（手动复制文本）

#### 4. 命令未识别
- 检查关键词是否在虚拟命令列表中
- 验证命令是否在正确的组中
- 检查回退链

#### 5. 模型未找到
- 确保模型名称在支持的模型列表中
- 检查BiosimulationModels.txt文件
- 验证模型名称拼写

#### 6. 下载/分析失败
- 检查网络连接
- 验证模型在BIGG数据库中存在
- 检查文件权限

### 调试命令

使用这些命令调试系统：

```python
# 测试命令检测
python -c "from main import main; main(initialize_only=True)"

# 测试虚拟命令匹配
python -c "from agent.virtual_command_agent import VirtualCommandAgent; agent = VirtualCommandAgent(); print(agent.match_command('download e_coli_core'))"

# 测试模型分析器
python -c "from agent.model_analyzer_agent import ModelAnalyzerAgent; analyzer = ModelAnalyzerAgent(); print(analyzer.run('analyse e_coli_core'))"
```

---

## 7. 未来改进

### 性能优化
- 优化重试参数
- 改进选择器策略
- 减少内存使用

### 功能扩展
- 支持更多模型类型
- 添加模型预览功能
- 实现批量模型选择
- 支持更多文件格式
- 添加验证和校验

### 用户体验
- 添加进度指示器
- 改进错误提示
- 支持键盘快捷键
- 交互式网络可视化
- 代谢通量分析
- 模型比较工具
- 导出为SBML格式
- 与代谢数据库集成
- 通路分析功能

---

## 8. 优势总结

### 1. 更好的用户体验
- 不会因为模型名称错误而中断用户操作
- 提供平滑的命令回退机制
- 保持对话的连续性

### 2. 更灵活的命令处理
- 支持混合输入（模型选择 + 其他命令）
- 允许用户在模型选择失败后继续其他操作
- 减少用户重新输入的需要

### 3. 更健壮的系统
- 处理边界情况和错误输入
- 提供有意义的错误信息
- 保持系统的响应性

### 4. 完整的可视化功能
- 生成多种类型的图表
- 创建美观的HTML报告
- 提供数据下载和预览功能

---

## 结论

BioLLM系统通过命令分组和回退机制提供了一个健壮、用户友好的界面。基于优先级的方法确保具有虚拟命令识别的特殊命令首先得到处理，而全面的回退链保证用户始终收到有意义的响应。系统集成了完整的生物仿真模型分析功能，包括下载、分析和可视化，为用户提供了强大的代谢网络分析工具。 