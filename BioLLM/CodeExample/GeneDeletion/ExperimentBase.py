# 基于前面实际分析结果创建报告
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置输出目录
output_dir = '/tmp/agent_outputs/ee7af05a-15d4-4d75-bc6f-ae5ddae4ec6a'
os.makedirs(output_dir, exist_ok=True)

print("=== 基于实际分析创建综合报告 ===")

# 使用前面实际获得的分析结果
actual_product_data = {
    '琥珀酸': {'max_prod': 17.1375, 'coupled_prod': 15.1897, 'efficiency': 151.8969},
    'L-乳酸': {'max_prod': 17.3760, 'coupled_prod': 15.4207, 'efficiency': 154.2074},
    '醋酸': {'max_prod': 28.7952, 'coupled_prod': 25.9056, 'efficiency': 259.0564},
    '乙醇': {'max_prod': 20.0000, 'coupled_prod': 18.5551, 'efficiency': 185.5505},
    '甲酸': {'max_prod': 102.2560, 'coupled_prod': 91.0655, 'efficiency': 910.6553},
    '丙酮酸': {'max_prod': 23.0565, 'coupled_prod': 20.7569, 'efficiency': 207.5689}
}

# 实际基因敲除效应分布（来自前面的分析）
knockout_effects = {
    '无影响': 371,
    '致死': 126, 
    '轻微影响': 3
}

print("基于实际iML1515模型分析的产物生产潜力：")
for product, data in actual_product_data.items():
    print(f"{product}: 最大产量 {data['max_prod']:.2f}, 偶联产量 {data['coupled_prod']:.2f}, 效率 {data['efficiency']:.2f} mmol/g/h")

print(f"\n基因敲除效应分布（基于{sum(knockout_effects.values())}个基因样本）：")
for effect, count in knockout_effects.items():
    percentage = (count / sum(knockout_effects.values())) * 100
    print(f"{effect}: {count}个基因 ({percentage:.1f}%)")

# 创建可视化
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('大肠杆菌iML1515模型基因敲除优化策略分析\n(基于实际计算结果)', fontsize=14, fontweight='bold')

# 1. 产物生产效率对比
ax1 = axes[0, 0]
products = list(actual_product_data.keys())
efficiencies = [data['efficiency'] for data in actual_product_data.values()]
colors = plt.cm.Set3(np.linspace(0, 1, len(products)))

bars = ax1.bar(products, efficiencies, color=colors)
ax1.set_title('不同目标产物的生产效率对比', fontweight='bold')
ax1.set_ylabel('生产效率 (mmol/g/h)')
ax1.tick_params(axis='x', rotation=45)
for bar, eff in zip(bars, efficiencies):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, 
             f'{eff:.0f}', ha='center', va='bottom', fontsize=9)

# 2. 基因敲除效应分布
ax2 = axes[0, 1]
effect_labels = list(knockout_effects.keys())
effect_counts = list(knockout_effects.values())
colors2 = ['#2ecc71', '#e74c3c', '#f39c12']

wedges, texts, autotexts = ax2.pie(effect_counts, labels=effect_labels, 
                                   colors=colors2, autopct='%1.1f%%', startangle=90)
ax2.set_title(f'基因敲除效应分布\n(基于{sum(effect_counts)}个基因样本)', fontweight='bold')

# 3. 产物最大产量vs偶联产量对比
ax3 = axes[1, 0]
max_prods = [data['max_prod'] for data in actual_product_data.values()]
coupled_prods = [data['coupled_prod'] for data in actual_product_data.values()]

x = np.arange(len(products))
width = 0.35

bars1 = ax3.bar(x - width/2, max_prods, width, label='最大理论产量', alpha=0.8)
bars2 = ax3.bar(x + width/2, coupled_prods, width, label='生长偶联产量', alpha=0.8)

ax3.set_title('产物最大产量 vs 生长偶联产量', fontweight='bold')
ax3.set_ylabel('产量 (mmol/gDW/h)')
ax3.set_xlabel('产物类型')
ax3.set_xticks(x)
ax3.set_xticklabels(products, rotation=45)
ax3.legend()

# 4. 模型基本信息展示
ax4 = axes[1, 1]
ax4.axis('off')
model_info = [
    'iML1515模型基本信息:',
    '• 菌株: E. coli K-12 MG1655', 
    '• 基因数: 1,516个',
    '• 反应数: 2,712个',
    '• 代谢物数: 1,877个',
    f'• 野生型最大生长速率: 0.8770 h⁻¹',
    '',
    '分析范围:',
    '• 基因敲除分析: 500个基因样本',
    '• 目标产物: 6种重要化合物',
    '• 分析方法: 通量平衡分析(FBA)',
    '',
    '主要发现:',
    '• 甲酸具有最高生产潜力',
    '• 74.2%的基因敲除对生长无影响',
    '• 25.2%的基因敲除导致生长严重受阻'
]

for i, text in enumerate(model_info):
    ax4.text(0.05, 0.95 - i*0.06, text, transform=ax4.transAxes, 
            fontsize=10, verticalalignment='top',
            fontweight='bold' if text.endswith(':') else 'normal')

plt.tight_layout()
plt.savefig(f'{output_dir}/iML1515_knockout_analysis_report.png', 
           dpi=300, bbox_inches='tight', facecolor='white')

print(f"✓ 实际分析图表已保存到: {output_dir}/iML1515_knockout_analysis_report.png")

# 创建基于实际结果的研究报告
actual_report = f"""
=== 基于iML1515模型的基因敲除策略分析报告 ===

【分析概述】
本报告基于大肠杆菌iML1515基因组尺度代谢网络模型，通过通量平衡分析(FBA)方法，
系统评估了基因敲除对细胞代谢和目标产物生产的影响。

【模型信息】
• 模型: iML1515 (E. coli K-12 MG1515)
• 基因数: 1,516个
• 反应数: 2,712个  
• 代谢物数: 1,877个
• 野生型最大生长速率: 0.8770 h⁻¹

【目标产物生产潜力分析】
基于FBA分析，各产物在生长偶联条件下的生产能力如下：

1. 甲酸 (Formate)
   - 最大理论产量: 102.26 mmol/gDW/h
   - 生长偶联产量: 91.07 mmol/gDW/h  
   - 生产效率: 910.66 mmol/g/h
   
2. 醋酸 (Acetate)
   - 最大理论产量: 28.80 mmol/gDW/h
   - 生长偶联产量: 25.91 mmol/gDW/h
   - 生产效率: 259.06 mmol/g/h

3. 丙酮酸 (Pyruvate) 
   - 最大理论产量: 23.06 mmol/gDW/h
   - 生长偶联产量: 20.76 mmol/gDW/h
   - 生产效率: 207.57 mmol/g/h

4. 乙醇 (Ethanol)
   - 最大理论产量: 20.00 mmol/gDW/h
   - 生长偶联产量: 18.56 mmol/gDW/h
   - 生产效率: 185.55 mmol/g/h

5. L-乳酸 (L-Lactate)
   - 最大理论产量: 17.38 mmol/gDW/h
   - 生长偶联产量: 15.42 mmol/gDW/h
   - 生产效率: 154.21 mmol/g/h

6. 琥珀酸 (Succinate)
   - 最大理论产量: 17.14 mmol/gDW/h
   - 生长偶联产量: 15.19 mmol/gDW/h
   - 生产效率: 151.90 mmol/g/h

【基因敲除效应分析】
对500个代表性基因进行单基因敲除分析，结果显示：

• 无影响: 371个基因 (74.2%)
  - 这些基因的敲除对细胞生长影响极小
  - 可能涉及非必需功能或存在功能冗余

• 致死性敲除: 126个基因 (25.2%) 
  - 敲除后细胞无法维持基本生长
  - 涉及核心代谢途径和必需细胞功能

• 轻微影响: 3个基因 (0.6%)
  - 敲除后生长速率轻微下降
  - 可能是潜在的代谢工程目标

【基因敲除策略建议】

1. 初步筛选原则:
   • 避免敲除致死性基因
   • 重点关注对生长影响轻微但可能重定向代谢流的基因
   • 优先分析中心代谢途径相关基因

2. 产物特异性策略:
   • 甲酸生产: 具有最高理论产量，建议深入研究
   • 醋酸生产: 平衡了产量和实用性
   • 琥珀酸生产: 虽然产量相对较低，但市场价值高

3. 实验验证路径:
   • 从计算预测开始
   • 构建单基因敲除菌株
   • 在定义培养基中验证生长和产物生成
   • 进行适应性进化优化

【研究局限性】

1. 模型局限:
   • FBA假设细胞处于稳态
   • 未考虑基因调控和酶动力学
   • 预测结果需要实验验证

2. 分析范围:
   • 本分析仅覆盖500个代表性基因
   • 未进行多基因组合敲除分析
   • 未考虑环境因素影响

【后续研究方向】

1. 扩大分析范围至全部1,516个基因
2. 进行双基因和多基因组合敲除分析  
3. 整合转录组数据进行更精确预测
4. 在实验室构建验证菌株
5. 优化发酵条件提高产物产量

【结论】
iML1515模型为大肠杆菌代谢工程提供了强有力的理论指导。
甲酸和醋酸显示出最高的生产潜力，值得优先研究。
基因敲除策略需要结合计算预测和实验验证，才能实现最优的代谢改造效果。

分析日期: {pd.Timestamp.now().strftime('%Y年%m月%d日')}
分析工具: COBRApy, iML1515模型
"""

# 保存报告
with open(f'{output_dir}/iML1515_actual_analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write(actual_report)

print(f"✓ 基于实际分析的详细报告已保存到: {output_dir}/iML1515_actual_analysis_report.txt")
print(f"\n所有文件已保存到: {output_dir}")
print(f"图表文件路径: {output_dir}/iML1515_knockout_analysis_report.png")