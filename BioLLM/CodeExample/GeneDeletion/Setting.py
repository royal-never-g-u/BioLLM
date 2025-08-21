# 导入必要的库
import cobra
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 加载iML1515模型
print("=== 加载iML1515大肠杆菌代谢网络模型 ===")
try:
    model = cobra.io.load_model("iML1515")
    print(f"✓ 模型加载成功")
    print(f"  - 反应数量: {len(model.reactions)}")
    print(f"  - 代谢物数量: {len(model.metabolites)}")
    print(f"  - 基因数量: {len(model.genes)}")
except Exception as e:
    print(f"错误: {e}")
    
# 检查模型基本信息
print(f"\n=== 模型基础代谢能力测试 ===")
solution = model.optimize()
print(f"野生型最大生长速率: {solution.objective_value:.4f} h⁻¹")

# 检查生物量反应
biomass_reactions = [rxn for rxn in model.reactions if 'biomass' in rxn.id.lower()]
print(f"生物量反应: {[rxn.id for rxn in biomass_reactions]}")

# 保存输出目录路径
output_dir = '/tmp/agent_outputs/ee7af05a-15d4-4d75-bc6f-ae5ddae4ec6a'
print(f"\n输出文件将保存到: {output_dir}")