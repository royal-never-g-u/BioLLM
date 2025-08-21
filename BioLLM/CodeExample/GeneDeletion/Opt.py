# 产物优化分析
print("=== 目标产物优化分析 ===")

def analyze_product_optimization(model, target_products=None):
    """
    分析不同产物的生产潜力和优化策略
    """
    if target_products is None:
        # 选择一些重要的生物技术产物
        target_products = {
            'EX_succ_e': '琥珀酸 (Succinate)', 
            'EX_lac__L_e': 'L-乳酸 (L-Lactate)',
            'EX_ac_e': '醋酸 (Acetate)',
            'EX_etoh_e': '乙醇 (Ethanol)',
            'EX_for_e': '甲酸 (Formate)',
            'EX_pyr_e': '丙酮酸 (Pyruvate)'
        }
    
    results = {}
    wild_type_growth = model.optimize().objective_value
    
    for product_id, product_name in target_products.items():
        print(f"\n--- 分析目标产物: {product_name} ({product_id}) ---")
        
        try:
            with model:
                # 设置产物为目标函数
                if product_id in [rxn.id for rxn in model.reactions]:
                    product_rxn = model.reactions.get_by_id(product_id)
                    
                    # 优化产物生产
                    model.objective = product_rxn
                    solution = model.optimize()
                    
                    max_production = solution.objective_value if solution.status == 'optimal' else 0
                    
                    # 在保持最小生长条件下优化产物
                    biomass_rxn = model.reactions.BIOMASS_Ec_iML1515_core_75p37M
                    biomass_rxn.lower_bound = 0.1  # 最小生长速率约束
                    
                    coupled_solution = model.optimize()
                    coupled_production = coupled_solution.objective_value if coupled_solution.status == 'optimal' else 0
                    coupled_growth = coupled_solution.fluxes['BIOMASS_Ec_iML1515_core_75p37M']
                    
                    results[product_id] = {
                        'product_name': product_name,
                        'max_production': max_production,
                        'coupled_production': coupled_production,
                        'coupled_growth': coupled_growth,
                        'production_efficiency': coupled_production / coupled_growth if coupled_growth > 0 else 0
                    }
                    
                    print(f"  最大理论产量: {max_production:.4f} mmol/gDW/h")
                    print(f"  生长偶联产量: {coupled_production:.4f} mmol/gDW/h")
                    print(f"  偶联生长速率: {coupled_growth:.4f} h⁻¹")
                    print(f"  生产效率: {coupled_production/coupled_growth:.4f} mmol/g/h" if coupled_growth > 0 else "  生产效率: N/A")
                else:
                    print(f"  警告: 产物反应 {product_id} 未在模型中找到")
                    
        except Exception as e:
            print(f"  错误: {e}")
            results[product_id] = None
    
    return results

# 分析目标产物
product_analysis = analyze_product_optimization(model)

# 创建产物分析结果表
print(f"\n=== 产物生产潜力汇总 ===")
product_df = pd.DataFrame([
    {
        '产物': data['product_name'],
        '最大产量 (mmol/gDW/h)': data['max_production'],
        '生长偶联产量 (mmol/gDW/h)': data['coupled_production'],
        '偶联生长速率 (h⁻¹)': data['coupled_growth'],
        '生产效率 (mmol/g/h)': data['production_efficiency']
    }
    for product_id, data in product_analysis.items() 
    if data is not None
])

print(product_df.round(4).to_string(index=False))