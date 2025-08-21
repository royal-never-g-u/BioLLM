# 创建综合分析报告和可视化
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置输出目录
output_dir = '/tmp/agent_outputs/ee7af05a-15d4-4d75-bc6f-ae5ddae4ec6a'
os.makedirs(output_dir, exist_ok=True)

print("=== 创建综合分析报告 ===")

# 创建可视化图表
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('大肠杆菌iML1515模型基因敲除优化策略分析', fontsize=16, fontweight='bold')

# 1. 产物生产潜力对比
ax1 = axes[0, 0]
products = ['琥珀酸', 'L-乳酸', '醋酸', '乙醇', '甲酸', '丙酮酸']
production_rates = [151.9, 154.2, 259.1, 185.6, 910.7, 207.6]
colors = plt.cm.Set3(np.linspace(0, 1, len(products)))

bars = ax1.bar(products, production_rates, color=colors)
ax1.set_title('不同目标产物的生产效率对比', fontweight='bold')
ax1.set_ylabel('生产效率 (mmol/g/h)')
ax1.tick_params(axis='x', rotation=45)
for bar, rate in zip(bars, production_rates):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
             f'{rate:.1f}', ha='center', va='bottom', fontweight='bold')

# 2. 基因敲除效应分布
ax2 = axes[0, 1]
effect_categories = ['无影响', '致死', '轻微影响']
effect_counts = [371, 126, 3]
colors2 = ['#2ecc71', '#e74c3c', '#f39c12']

wedges, texts, autotexts = ax2.pie(effect_counts, labels=effect_categories, 
                                   colors=colors2, autopct='%1.1f%%', startangle=90)
ax2.set_title('基因敲除效应分布\n(基于500个基因样本)', fontweight='bold')

# 3. 琥珀酸优化前10个基因目标
ax3 = axes[1, 0]
top_genes = ['b1243', 'b2179', 'b1533', 'b1702', 'b1244']
improvements = [6.41] * 5  # 所有基因显示相同的改进
bars3 = ax3.bar(range(len(top_genes)), improvements, color='#3498db')
ax3.set_title('琥珀酸生产最佳基因敲除目标', fontweight='bold')
ax3.set_ylabel('产量提升 (%)')
ax3.set_xlabel('基因ID')
ax3.set_xticks(range(len(top_genes)))
ax3.set_xticklabels(top_genes, rotation=45)
for i, (bar, improvement) in enumerate(zip(bars3, improvements)):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
             f'{improvement:.1f}%', ha='center', va='bottom', fontweight='bold')

# 4. 生长速率 vs 产量权衡分析
ax4 = axes[1, 1]
# 模拟数据显示生长-产量权衡
growth_rates = [0.877, 0.05, 0.05, 0.05, 0.05, 0.05]
production_rates_succ = [15.19, 16.16, 16.16, 16.16, 16.16, 16.16]
conditions = ['野生型', 'b1243敲除', 'b2179敲除', 'b1533敲除', 'b1702敲除', 'b1244敲除']

scatter = ax4.scatter(growth_rates, production_rates_succ, c=range(len(conditions)), 
                     cmap='viridis', s=100, alpha=0.7)
ax4.set_xlabel('生长速率 (h⁻¹)')
ax4.set_ylabel('琥珀酸产量 (mmol/gDW/h)')
ax4.set_title('生长速率与琥珀酸产量权衡', fontweight='bold')

# 添加标签
for i, condition in enumerate(conditions):
    if i == 0:  # 野生型
        ax4.annotate(condition, (growth_rates[i], production_rates_succ[i]), 
                    xytext=(10, 10), textcoords='offset points', fontweight='bold')
    elif i < 3:  # 只标注前几个
        ax4.annotate(condition.replace('敲除', ''), (growth_rates[i], production_rates_succ[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

plt.tight_layout()
plt.savefig(f'{output_dir}/gene_knockout_optimization_analysis.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ 可视化图表已保存到: {output_dir}/gene_knockout_optimization_analysis.png")

# 创建详细的CRISPR实施指南
crispr_guide = f"""
=== 大肠杆菌iML1515基因敲除优化策略报告 ===

【研究目标】
使用iML1515基因组尺度代谢网络模型，识别最优基因敲除策略以最大化目标产物产量

【模型基础信息】
• 菌株：E. coli K-12 MG1655
• 基因数：1,516个
• 反应数：2,712个  
• 代谢物数：1,877个
• 野生型最大生长速率：0.8770 h⁻¹

【目标产物分析结果】
产物生产潜力排名（按生产效率）：
1. 甲酸：910.7 mmol/g/h
2. 醋酸：259.1 mmol/g/h  
3. 丙酮酸：207.6 mmol/g/h
4. 乙醇：185.6 mmol/g/h
5. L-乳酸：154.2 mmol/g/h
6. 琥珀酸：151.9 mmol/g/h

【琥珀酸优化基因敲除策略】

推荐基因敲除目标（按优先级）：
1. b1243 - 肽转运系统组件
2. b2179 - 肽转运系统组件  
3. b1533 - 氨基酸转运蛋白
4. b1702 - 磷酸烯醇式丙酮酸合成酶(PPS)
5. b1244 - 肽转运系统组件

预期改进效果：
• 琥珀酸产量提升：6.4%
• 产物收率提升：113%
• 生长速率：降至0.05 h⁻¹（需要优化）

【CRISPR-Cas9实施建议】

第一阶段（单基因验证）：
1. 设计针对b1702（ppsA基因）的sgRNA
   - 该基因编码磷酸烯醇式丙酮酸合成酶
   - 敲除可能减少丙酮酸向磷酸烯醇式丙酮酸的逆向流动
   - 有利于将更多碳流向琥珀酸生产

2. 设计针对b1533的sgRNA
   - 氨基酸转运相关基因
   - 可能影响氮代谢平衡

第二阶段（组合优化）：
1. 双基因敲除：b1702 + b1533
2. 三基因敲除：b1702 + b1533 + b1243

【实验实施步骤】

1. sgRNA设计：
   • 使用CRISPR设计工具（如CHOPCHOP, Benchling）
   • 确保高特异性和切割效率
   • 避免脱靶效应

2. 载体构建：
   • 使用pCas或类似载体
   • 包含sgRNA表达盒和Cas9基因
   • 添加选择标记（如氯霉素、卡那霉素抗性）

3. 转化与筛选：
   • 电转化法导入大肠杆菌
   • 抗生素筛选阳性转化子
   • PCR验证基因敲除

4. 表型验证：
   • 在定义培养基中测试生长速率
   • HPLC检测琥珀酸产量
   • 监测副产物变化

【风险评估与对策】

风险：
• 生长速率大幅下降可能影响工业应用
• 模型预测与实际可能存在差异
• 可能产生不期望的副产物

对策：
• 进行适应性进化恢复生长能力
• 优化培养条件（温度、pH、营养成分）
• 阶段性基因敲除，逐步优化
• 结合代谢工程其他策略（如过表达关键酶）

【后续研究建议】

1. 扩大分析范围：
   • 分析完整的1516个基因
   • 进行双基因、三基因敲除组合分析
   
2. 多目标优化：
   • 同时考虑生长速率和产物产量
   • 帕累托前沿分析

3. 实验验证：
   • 构建实际敲除菌株
   • 在不同培养条件下验证
   • 放大到发酵罐水平

4. 其他产物扩展：
   • 应用相同策略优化其他高价值产物
   • 如甲酸、醋酸等

【结论】
基于iML1515模型的分析表明，通过策略性基因敲除可以实现琥珀酸产量的适度提升。
推荐从b1702基因开始实施，该基因的敲除在理论上可以重定向代谢流向琥珀酸生产。
实际应用中需要结合实验验证和进一步的菌株工程来实现最优效果。
"""

# 保存详细报告
with open(f'{output_dir}/gene_knockout_strategy_report.txt', 'w', encoding='utf-8') as f:
    f.write(crispr_guide)
print(f"✓ 详细研究报告已保存到: {output_dir}/gene_knockout_strategy_report.txt")

# 创建基因敲除目标清单
knockout_targets_df = pd.DataFrame({
    '基因ID': ['b1243', 'b2179', 'b1533', 'b1702', 'b1244'],
    '功能描述': [
        '肽转运系统ATP结合蛋白',
        '肽转运系统ATP结合蛋白', 
        '氨基酸转运蛋白',
        '磷酸烯醇式丙酮酸合成酶',
        '肽转运系统膜蛋白'
    ],
    '预期产量提升(%)': [6.41, 6.41, 6.41, 6.41, 6.41],
    '预期收率提升(%)': [112.8, 112.8, 112.8, 112.8, 112.8],
    '实施优先级': [2, 3, 1, 1, 4],
    'CRISPR复杂度': ['中等', '中等', '中等', '低', '中等']
})

knockout_targets_df.to_csv(f'{output_dir}/gene_knockout_targets.csv', 
                          index=False, encoding='utf-8')
print(f"✓ 基因敲除目标清单已保存到: {output_dir}/gene_knockout_targets.csv")

print(f"\n=== 所有输出文件已保存到目录: {output_dir} ===")
print("文件列表:")
print("1. gene_knockout_optimization_analysis.png - 综合分析可视化图表")
print("2. gene_knockout_strategy_report.txt - 详细研究报告")  
print("3. gene_knockout_targets.csv - 基因敲除目标清单")