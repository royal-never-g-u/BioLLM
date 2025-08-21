# 基因敲除分析框架
print("=== 基因敲除分析策略框架 ===")

def analyze_single_gene_knockout(model, gene_list=None, min_growth_rate=0.1):
    """
    分析单基因敲除对生长的影响
    """
    if gene_list is None:
        gene_list = [gene.id for gene in model.genes]
    
    results = []
    wild_type_growth = model.optimize().objective_value
    
    print(f"野生型生长速率: {wild_type_growth:.4f}")
    print(f"开始分析 {len(gene_list)} 个基因的敲除效应...")
    
    for i, gene_id in enumerate(gene_list):
        if i % 200 == 0:
            print(f"  已完成: {i}/{len(gene_list)} ({i/len(gene_list)*100:.1f}%)")
        
        try:
            # 进行基因敲除
            with model:
                gene = model.genes.get_by_id(gene_id)
                gene.knock_out()
                solution = model.optimize()
                
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                growth_ratio = growth_rate / wild_type_growth if wild_type_growth > 0 else 0
                
                # 分类基因敲除效应
                if growth_rate < min_growth_rate:
                    effect = "致死" if growth_rate < 0.01 else "严重影响"
                elif growth_ratio < 0.8:
                    effect = "中等影响"
                elif growth_ratio < 0.95:
                    effect = "轻微影响"
                else:
                    effect = "无影响"
                
                results.append({
                    'gene_id': gene_id,
                    'growth_rate': growth_rate,
                    'growth_ratio': growth_ratio,
                    'growth_reduction': (1 - growth_ratio) * 100,
                    'effect_category': effect,
                    'reactions_affected': len([rxn for rxn in gene.reactions])
                })
        
        except Exception as e:
            results.append({
                'gene_id': gene_id,
                'growth_rate': 0,
                'growth_ratio': 0,
                'growth_reduction': 100,
                'effect_category': "分析错误",
                'reactions_affected': 0
            })
    
    return pd.DataFrame(results)

# 进行基因敲除分析（为了演示，我们先分析前500个基因）
print("\n=== 开始基因敲除分析 ===")
sample_genes = [gene.id for gene in model.genes][:500]  # 演示用，实际可以分析所有基因
knockout_results = analyze_single_gene_knockout(model, sample_genes)

print(f"\n=== 基因敲除分析结果汇总 ===")
print(f"总分析基因数: {len(knockout_results)}")
print(f"\n不同敲除效应的基因分布:")
effect_counts = knockout_results['effect_category'].value_counts()
for effect, count in effect_counts.items():
    percentage = (count / len(knockout_results)) * 100
    print(f"  {effect}: {count} 个基因 ({percentage:.1f}%)")