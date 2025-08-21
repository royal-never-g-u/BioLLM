# 针对特定产物的基因敲除策略分析
print("=== 琥珀酸生产基因敲除优化策略 ===")

def find_knockout_targets_for_product(model, target_product='EX_succ_e', candidate_genes=None):
    """
    寻找能够提高特定产物产量的基因敲除目标
    """
    if candidate_genes is None:
        # 重点分析与中心代谢相关的基因
        central_metabolism_genes = []
        
        # 糖酵解和TCA循环相关反应的基因
        key_pathways = ['pgi', 'pfk', 'fba', 'tpi', 'gapdh', 'pyk', 'eno',  # 糖酵解
                       'cs', 'acont', 'icd', 'akgdh', 'sucoas', 'sdh', 'fum', 'mdh',  # TCA
                       'ppc', 'pck', 'mae', 'pps',  # 磷酸烯醇式丙酮酸相关
                       'ack', 'pta', 'ldh', 'adh', 'pfl']  # 发酵途径
        
        for rxn in model.reactions:
            if any(pathway in rxn.id.lower() for pathway in key_pathways):
                central_metabolism_genes.extend([gene.id for gene in rxn.genes])
        
        candidate_genes = list(set(central_metabolism_genes))[:100]  # 限制分析数量
    
    print(f"分析 {len(candidate_genes)} 个候选基因对琥珀酸生产的影响...")
    
    # 获取野生型基线
    with model:
        model.objective = target_product
        biomass_constraint = model.reactions.BIOMASS_Ec_iML1515_core_75p37M
        biomass_constraint.lower_bound = 0.1
        
        wt_solution = model.optimize()
        wt_production = wt_solution.objective_value if wt_solution.status == 'optimal' else 0
        wt_growth = wt_solution.fluxes['BIOMASS_Ec_iML1515_core_75p37M'] if wt_solution.status == 'optimal' else 0
    
    print(f"野生型琥珀酸产量: {wt_production:.4f} mmol/gDW/h")
    print(f"野生型生长速率: {wt_growth:.4f} h⁻¹")
    
    knockout_results = []
    
    for i, gene_id in enumerate(candidate_genes):
        if i % 20 == 0:
            print(f"  进度: {i}/{len(candidate_genes)} ({i/len(candidate_genes)*100:.1f}%)")
        
        try:
            with model:
                # 基因敲除
                gene = model.genes.get_by_id(gene_id)
                gene.knock_out()
                
                # 设置目标和约束
                model.objective = target_product
                biomass_constraint = model.reactions.BIOMASS_Ec_iML1515_core_75p37M
                biomass_constraint.lower_bound = 0.05  # 允许更低的生长速率
                
                solution = model.optimize()
                
                if solution.status == 'optimal':
                    production = solution.objective_value
                    growth = solution.fluxes['BIOMASS_Ec_iML1515_core_75p37M']
                    
                    production_improvement = ((production - wt_production) / wt_production) * 100 if wt_production > 0 else 0
                    yield_improvement = (production / growth - wt_production / wt_growth) / (wt_production / wt_growth) * 100 if wt_growth > 0 and growth > 0 else 0
                    
                    knockout_results.append({
                        'gene_id': gene_id,
                        'production': production,
                        'growth': growth,
                        'production_improvement': production_improvement,
                        'yield': production / growth if growth > 0 else 0,
                        'yield_improvement': yield_improvement,
                        'viable': growth >= 0.05
                    })
                else:
                    knockout_results.append({
                        'gene_id': gene_id,
                        'production': 0,
                        'growth': 0,
                        'production_improvement': -100,
                        'yield': 0,
                        'yield_improvement': -100,
                        'viable': False
                    })
                    
        except Exception as e:
            print(f"  基因 {gene_id} 分析错误: {e}")
    
    return pd.DataFrame(knockout_results), wt_production, wt_growth

# 执行琥珀酸优化分析
knockout_df, baseline_production, baseline_growth = find_knockout_targets_for_product(model)

print(f"\n=== 基因敲除分析结果 ===")
print(f"有效敲除目标: {len(knockout_df[knockout_df['viable']])} / {len(knockout_df)}")

# 筛选有益的基因敲除
beneficial_knockouts = knockout_df[
    (knockout_df['viable']) & 
    (knockout_df['production_improvement'] > 5)  # 至少5%的产量提升
].sort_values('production_improvement', ascending=False)

print(f"\n=== 前10个最佳基因敲除目标 ===")
if len(beneficial_knockouts) > 0:
    top_targets = beneficial_knockouts.head(10)[['gene_id', 'production', 'growth', 'production_improvement', 'yield_improvement']]
    print(top_targets.round(4).to_string(index=False))
else:
    print("未发现显著有益的单基因敲除目标")
    
    # 显示影响较小但可能有用的目标
    moderate_targets = knockout_df[
        (knockout_df['viable']) & 
        (knockout_df['production_improvement'] > -10)
    ].sort_values('production_improvement', ascending=False).head(10)
    
    print(f"\n=== 影响较小的敲除目标（参考） ===")
    if len(moderate_targets) > 0:
        print(moderate_targets[['gene_id', 'production', 'growth', 'production_improvement', 'yield_improvement']].round(4).to_string(index=False))