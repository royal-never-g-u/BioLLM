#!/usr/bin/env python3
"""
分析类型定义和任务提示
"""

# 定义分析类型字典
ANALYSIS_TYPES = {
    1: "Flux Balance Analysis (FBA)",
    2: "Gene Knockout Analysis", 
    3: "Phenotype Prediction",
    4: "Pathway Analysis",
    5: "Evolutionary Analysis",
    6: "Constraint-Based Analysis"
}

# 任务提示说明文字
TASK_PROMPT = """
请根据提供的代谢网络模型数据，执行以下分析任务：

1. **Flux Balance Analysis (FBA)**: 
   - 分析代谢网络中的通量分布
   - 计算最优生长条件下的代谢通量
   - 识别关键代谢反应和瓶颈

2. **Gene Knockout Analysis**: 
   - 模拟基因敲除对细胞生长的影响
   - 识别必需基因和非必需基因
   - 分析基因敲除对代谢产物合成的影响

3. **Phenotype Prediction**: 
   - 预测不同环境条件下的细胞表型
   - 分析营养限制对生长的影响
   - 预测代谢产物的产量变化

4. **Pathway Analysis**: 
   - 识别关键代谢途径
   - 分析途径的冗余性和重要性
   - 评估途径对细胞功能的贡献

5. **Evolutionary Analysis**: 
   - 分析代谢网络的进化特征
   - 比较不同物种的代谢能力
   - 预测进化趋势和适应性

6. **Constraint-Based Analysis**: 
   - 基于约束条件的代谢网络分析
   - 考虑环境限制和生理约束
   - 优化代谢网络性能

请根据模型的具体特征和用户需求，选择合适的分析类型，并提供详细的分析结果和可视化图表。
"""

# 获取分析类型描述的函数
def get_analysis_type_description(analysis_id: int) -> str:
    """
    根据分析ID获取分析类型描述
    
    Args:
        analysis_id (int): 分析类型ID (1-6)
        
    Returns:
        str: 分析类型描述，如果ID不存在则返回None
    """
    return ANALYSIS_TYPES.get(analysis_id)

# 获取所有分析类型的函数
def get_all_analysis_types() -> dict:
    """
    获取所有分析类型
    
    Returns:
        dict: 包含所有分析类型的字典
    """
    return ANALYSIS_TYPES.copy()

# 验证分析ID是否有效的函数
def is_valid_analysis_id(analysis_id: int) -> bool:
    """
    验证分析ID是否有效
    
    Args:
        analysis_id (int): 要验证的分析ID
        
    Returns:
        bool: 如果ID有效返回True，否则返回False
    """
    return analysis_id in ANALYSIS_TYPES

# 获取任务提示的函数
def get_task_prompt() -> str:
    """
    获取任务提示说明文字
    
    Returns:
        str: 任务提示说明文字
    """
    return TASK_PROMPT

# 示例使用
if __name__ == "__main__":
    print("=== 分析类型字典 ===")
    for key, value in ANALYSIS_TYPES.items():
        print(f"{key}: {value}")
    
    print("\n=== 任务提示 ===")
    print(TASK_PROMPT)
    
    print("\n=== 函数测试 ===")
    print(f"分析类型1的描述: {get_analysis_type_description(1)}")
    print(f"分析类型7是否有效: {is_valid_analysis_id(7)}")
    print(f"分析类型3是否有效: {is_valid_analysis_id(3)}")
