# BioLLM

一个基于LangChain和Qwen-Plus API的多功能AI代码助手，支持Python/Matlab代码生成、解释、调试、执行、联网搜索、RAG知识增强和记忆功能，CLI交互。特别针对生物仿真模型分析进行了优化。

> 📖 **详细文档**: 查看 [COMPREHENSIVE_DOCUMENTATION.md](COMPREHENSIVE_DOCUMENTATION.md) 获取完整的功能说明和使用指南。

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

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动应用
```bash
# CLI模式
python main.py

# Streamlit模式
streamlit run app.py
```

### 配置
- 在`.env`中填写Qwen-Plus API Key等信息
- 本地知识库请放入`knowledge_base/`目录

## 使用示例

### 模型下载
```
download e_coli_core
I want to download the iMM904 model
```

### 模型分析
```
analyse e_coli_core
Please analyze the iMM904 model
```

### 代码生成
```
generate a Python script for metabolic analysis
```

### 知识查询
```
knowledge What are metabolic models?
```

## 文档

- 📖 [完整功能文档](COMPREHENSIVE_DOCUMENTATION.md) - 详细的功能说明、使用指南和技术实现
- 🔧 [故障排除](COMPREHENSIVE_DOCUMENTATION.md#6-故障排除) - 常见问题和解决方案
- 🚀 [未来改进](COMPREHENSIVE_DOCUMENTATION.md#7-未来改进) - 计划中的功能增强

## 贡献

欢迎提交Issue和Pull Request来改进BioLLM项目。

## 许可证

本项目采用MIT许可证。 