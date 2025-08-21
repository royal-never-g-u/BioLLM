# 分析最佳基因敲除目标的功能和CRISPR实施策略
print("=== 最佳基因敲除目标功能分析 ===")

def analyze_gene_functions(model, gene_list):
    """
    分析基因功能和相关反应
    """
    gene_info = []
    
    for gene_id in gene_list:
        try:
            gene = model.genes.get_by_id(gene_id)
            
            # 获取基因相关的反应
            reactions = [rxn.id for rxn in gene.reactions]
            reaction_names = [rxn.name for rxn in gene.reactions]
            
            # 分析反应类型
            pathway_involvement = []
            for rxn in gene.reactions:
                rxn_id_lower = rxn.id.lower()
                if any(keyword in rxn_id_lower for keyword in ['pgi', 'pfk', 'fba', 'gapdh', 'pyk']):
                    pathway_involvement.append('糖酵解')
                elif any(keyword in rxn_id_lower for keyword in ['cs', 'icd', 'akgdh', 'sucoas', 'sdh', 'fum', 'mdh']):
                    pathway_involvement.append('TCA循环')
                elif any(keyword in rxn_id_lower for keyword in ['ack', 'pta', 'ldh', 'adh', 'pfl']):
                    pathway_involvement.append('发酵途径')
                elif any(keyword in rxn_id_lower for keyword in ['ppc', 'pck', 'mae']):
                    pathway_involvement.append('磷酸烯醇式丙酮酸代谢')
                elif 'transport' in rxn_id_lower or 'ex_' in rxn_id_lower:
                    pathway_involvement.append('转运')
            
            gene_info.append({
                'gene_id': gene_id,
                'reactions_count': len(reactions),
                'reactions': ', '.join(reactions[:3]) + ('...' if len(reactions) > 3 else ''),
                'pathways': ', '.join(list(set(pathway_involvement))) if pathway_involvement else '其他代谢',
                'reaction_names': ', '.join(reaction_names[:2]) + ('...' if len(reaction_names) > 2 else '')
            })
            
        except Exception as e:
            gene_info.append({
                'gene_id': gene_id,
                'reactions_count': 0,
                'reactions': '未知',
                'pathways': '分析错误',
                'reaction_names': f'错误: {e}'
            })
    
    return pd.DataFrame(gene_info)

# 分析前10个最佳基因目标
top_gene_ids = ['b1243', 'b2179', 'b1533', 'b1702', 'b1244', 'b0928', 'b1745', 'b4035', 'b2263', 'b2458']
gene_function_df = analyze_gene_functions(model, top_gene_ids)

print("基因功能分析结果:")
print(gene_function_df.to_string(index=False))

# CRISPR实施建议
print(f"\n=== CRISPR-Cas9基因敲除实施建议 ===")

crispr_recommendations = {
    '目标产物': '琥珀酸 (Succinate)',
    '预期产量提升': '~6.4%',
    '预期收率提升': '~113%',
    '推荐敲除基因': top_gene_ids[:3],  # 前3个基因
    '实施策略': [
        '1. 单基因敲除验证：先测试单个基因敲除效果',
        '2. 组合敲除：可尝试2-3个基因的组合敲除',
        '3. 分阶段实施：先敲除影响最小的基因，逐步优化',
        '4. 生长速率监控：确保敲除后菌株仍具有足够的生长能力'
    ],
    '注意事项': [
        '• 模型预测显示这些敲除会降低生长速率',
        '• 需要在实验中验证模型预测的准确性',
        '• 可能需要适应性进化来恢复生长能力',
        '• 建议同时监测其他副产物的变化'
    ]
}

for key, value in crispr_recommendations.items():
    print(f"\n{key}:")
    if isinstance(value, list):
        for item in value:
            print(f"  {item}")
    else:
        print(f"  {value}")