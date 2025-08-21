"""
Optimization Template for Gene Deletion Analysis

This template provides configurable product optimization analysis functionality.
Agent systems can customize the optimization process by modifying the configuration.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import warnings

# Import configuration template
from .config_template import (
    TARGET_PRODUCTS,
    OPTIMIZATION_CONSTRAINTS,
    PRODUCTION_OPTIMIZATION
)

warnings.filterwarnings('ignore')

class OptimizationTemplate:
    """
    Template class for product optimization analysis.
    Contains configurable slots for different optimization strategies.
    """
    
    def __init__(self, model, config_override=None):
        """
        Initialize the optimizer with a metabolic model.
        
        Args:
            model: COBRA metabolic model
            config_override (dict): Optional configuration override
        """
        self.model = model
        self.products_config = TARGET_PRODUCTS.copy()
        self.constraints_config = OPTIMIZATION_CONSTRAINTS.copy()
        self.optimization_config = PRODUCTION_OPTIMIZATION.copy()
        
        if config_override:
            self.products_config.update(config_override.get('target_products', {}))
            self.constraints_config.update(config_override.get('optimization_constraints', {}))
            self.optimization_config.update(config_override.get('production_optimization', {}))
        
        self.results = {}
        
    def analyze_product_optimization(self, target_products=None):
        """
        SLOT: Analyze product optimization - can be customized by agent.
        """
        print("=== 目标产物优化分析 ===")
        
        # SLOT: Product selection - agent can customize
        if target_products is None:
            target_products = self._get_default_target_products()
        
        # SLOT: Get wild type baseline - agent can customize
        wild_type_growth = self._get_wild_type_growth()
        
        results = {}
        
        for product_id, product_name in target_products.items():
            print(f"\n--- 分析目标产物: {product_name} ({product_id}) ---")
            
            # SLOT: Product optimization analysis - agent can customize
            result = self._analyze_single_product(product_id, product_name, wild_type_growth)
            results[product_id] = result
        
        # SLOT: Results processing - agent can customize
        self.results['product_optimization'] = results
        self._process_optimization_results(results)
        
        return results
    
    def _get_default_target_products(self):
        """
        SLOT: Get default target products - agent can customize.
        """
        # SLOT: Default product selection - agent can customize
        return {
            product_id: product_info['name']
            for product_id, product_info in self.products_config.items()
        }
    
    def _get_wild_type_growth(self):
        """
        SLOT: Get wild type growth rate - agent can customize.
        """
        # SLOT: Wild type growth calculation - agent can customize
        solution = self.model.optimize()
        return solution.objective_value if solution.status == 'optimal' else 0
    
    def _analyze_single_product(self, product_id, product_name, wild_type_growth):
        """
        SLOT: Analyze single product optimization - agent can customize.
        """
        try:
            # SLOT: Product optimization setup - agent can customize
            if product_id in [rxn.id for rxn in self.model.reactions]:
                product_rxn = self.model.reactions.get_by_id(product_id)
                
                # SLOT: Optimization method selection - agent can customize
                if self.optimization_config['optimization_method'] == 'FBA':
                    result = self._perform_fba_optimization(product_rxn, product_name)
                elif self.optimization_config['optimization_method'] == 'FVA':
                    result = self._perform_fva_optimization(product_rxn, product_name)
                else:
                    result = self._perform_custom_optimization(product_rxn, product_name)
                
                return result
            else:
                print(f"  警告: 产物反应 {product_id} 未在模型中找到")
                return None
                
        except Exception as e:
            print(f"  错误: {e}")
            return None
    
    def _perform_fba_optimization(self, product_rxn, product_name):
        """
        SLOT: Perform FBA optimization - agent can customize.
        """
        with self.model:
            # SLOT: Set objective function - agent can customize
            self.model.objective = product_rxn
            
            # SLOT: Apply optimization constraints - agent can customize
            self._apply_optimization_constraints()
            
            # SLOT: Perform optimization - agent can customize
            solution = self.model.optimize()
            
            max_production = solution.objective_value if solution.status == 'optimal' else 0
            
            # SLOT: Coupled optimization - agent can customize
            if self.optimization_config['couple_growth_production']:
                coupled_result = self._perform_coupled_optimization(product_rxn)
                result = {
                    'product_name': product_name,
                    'max_production': max_production,
                    **coupled_result
                }
            else:
                result = {
                    'product_name': product_name,
                    'max_production': max_production,
                    'coupled_production': max_production,
                    'coupled_growth': 0,
                    'production_efficiency': 0
                }
            
            # SLOT: Additional analysis - agent can customize
            additional_info = self._get_additional_product_info(product_rxn, solution)
            result.update(additional_info)
            
            return result
    
    def _perform_fva_optimization(self, product_rxn, product_name):
        """
        SLOT: Perform FVA optimization - agent can customize.
        """
        # SLOT: FVA optimization implementation - agent can implement
        raise NotImplementedError("FVA optimization not implemented")
    
    def _perform_custom_optimization(self, product_rxn, product_name):
        """
        SLOT: Perform custom optimization - agent can implement.
        """
        # SLOT: Custom optimization implementation - agent can implement
        raise NotImplementedError("Custom optimization not implemented")
    
    def _apply_optimization_constraints(self):
        """
        SLOT: Apply optimization constraints - agent can customize.
        """
        # SLOT: Constraint application logic - agent can customize
        
        # Apply biomass constraints
        if hasattr(self.model, 'reactions'):
            biomass_reactions = [rxn for rxn in self.model.reactions if 'biomass' in rxn.id.lower()]
            if biomass_reactions:
                biomass_rxn = biomass_reactions[0]
                biomass_rxn.lower_bound = self.constraints_config['min_biomass_rate']
                biomass_rxn.upper_bound = self.constraints_config['max_biomass_rate']
        
        # SLOT: Additional constraints - agent can add
        self._apply_custom_constraints()
    
    def _apply_custom_constraints(self):
        """
        SLOT: Apply custom constraints - agent can implement.
        """
        # SLOT: Custom constraint application - agent can add
        pass
    
    def _perform_coupled_optimization(self, product_rxn):
        """
        SLOT: Perform coupled growth-production optimization - agent can customize.
        """
        # SLOT: Coupled optimization logic - agent can customize
        biomass_reactions = [rxn for rxn in self.model.reactions if 'biomass' in rxn.id.lower()]
        
        if biomass_reactions:
            biomass_rxn = biomass_reactions[0]
            biomass_rxn.lower_bound = self.constraints_config['min_biomass_rate']
            
            solution = self.model.optimize()
            
            coupled_production = solution.objective_value if solution.status == 'optimal' else 0
            coupled_growth = solution.fluxes[biomass_rxn.id] if solution.status == 'optimal' else 0
            
            production_efficiency = coupled_production / coupled_growth if coupled_growth > 0 else 0
            
            return {
                'coupled_production': coupled_production,
                'coupled_growth': coupled_growth,
                'production_efficiency': production_efficiency
            }
        else:
            return {
                'coupled_production': 0,
                'coupled_growth': 0,
                'production_efficiency': 0
            }
    
    def _get_additional_product_info(self, product_rxn, solution):
        """
        SLOT: Get additional product information - agent can implement.
        """
        # SLOT: Additional information extraction - agent can add
        return {}
    
    def _process_optimization_results(self, results):
        """
        SLOT: Process optimization results - agent can customize.
        """
        print(f"\n=== 产物生产潜力汇总 ===")
        
        # SLOT: Results processing logic - agent can customize
        valid_results = {k: v for k, v in results.items() if v is not None}
        
        if valid_results:
            # SLOT: Create results table - agent can customize
            product_df = self._create_results_table(valid_results)
            print(product_df.round(4).to_string(index=False))
            
            # SLOT: Additional result processing - agent can add
            self._custom_result_processing(valid_results)
        else:
            print("没有有效的优化结果")
    
    def _create_results_table(self, valid_results):
        """
        SLOT: Create results table - agent can customize.
        """
        # SLOT: Table creation logic - agent can customize
        table_data = []
        
        for product_id, data in valid_results.items():
            table_data.append({
                '产物': data['product_name'],
                '最大产量 (mmol/gDW/h)': data['max_production'],
                '生长偶联产量 (mmol/gDW/h)': data['coupled_production'],
                '偶联生长速率 (h⁻¹)': data['coupled_growth'],
                '生产效率 (mmol/g/h)': data['production_efficiency']
            })
        
        return pd.DataFrame(table_data)
    
    def _custom_result_processing(self, valid_results):
        """
        SLOT: Custom result processing - agent can implement.
        """
        # SLOT: Custom processing logic - agent can add
        pass
    
    def rank_products_by_efficiency(self):
        """
        SLOT: Rank products by efficiency - agent can customize.
        """
        if 'product_optimization' not in self.results:
            print("No optimization results available. Run analyze_product_optimization first.")
            return None
        
        # SLOT: Ranking logic - agent can customize
        results = self.results['product_optimization']
        valid_results = {k: v for k, v in results.items() if v is not None}
        
        if not valid_results:
            return None
        
        # SLOT: Ranking criteria - agent can customize
        ranking_data = []
        for product_id, data in valid_results.items():
            ranking_data.append({
                'product_id': product_id,
                'product_name': data['product_name'],
                'efficiency': data['production_efficiency'],
                'max_production': data['max_production'],
                'coupled_production': data['coupled_production']
            })
        
        ranking_df = pd.DataFrame(ranking_data)
        ranking_df = ranking_df.sort_values('efficiency', ascending=False)
        
        return ranking_df
    
    def get_optimization_summary(self):
        """
        SLOT: Get optimization summary - agent can customize.
        """
        if 'product_optimization' not in self.results:
            return None
        
        # SLOT: Summary generation logic - agent can customize
        results = self.results['product_optimization']
        valid_results = {k: v for k, v in results.items() if v is not None}
        
        summary = {
            'total_products_analyzed': len(results),
            'successful_optimizations': len(valid_results),
            'top_product': None,
            'average_efficiency': 0,
            'efficiency_range': (0, 0)
        }
        
        if valid_results:
            efficiencies = [data['production_efficiency'] for data in valid_results.values()]
            summary['average_efficiency'] = np.mean(efficiencies)
            summary['efficiency_range'] = (min(efficiencies), max(efficiencies))
            
            # Find top product
            top_product = max(valid_results.items(), key=lambda x: x[1]['production_efficiency'])
            summary['top_product'] = {
                'product_id': top_product[0],
                'product_name': top_product[1]['product_name'],
                'efficiency': top_product[1]['production_efficiency']
            }
        
        return summary
    
    def export_optimization_results(self, output_path=None):
        """
        SLOT: Export optimization results - agent can customize.
        """
        if output_path is None:
            # SLOT: Default output path - agent can customize
            output_path = "product_optimization_results.csv"
        
        # SLOT: Export logic - agent can customize
        if 'product_optimization' in self.results:
            results = self.results['product_optimization']
            valid_results = {k: v for k, v in results.items() if v is not None}
            
            if valid_results:
                export_data = []
                for product_id, data in valid_results.items():
                    export_data.append({
                        'product_id': product_id,
                        'product_name': data['product_name'],
                        'max_production': data['max_production'],
                        'coupled_production': data['coupled_production'],
                        'coupled_growth': data['coupled_growth'],
                        'production_efficiency': data['production_efficiency']
                    })
                
                export_df = pd.DataFrame(export_data)
                export_df.to_csv(output_path, index=False, encoding='utf-8')
                print(f"✓ 优化结果已导出到: {output_path}")
            else:
                print("没有有效的优化结果可导出")
        else:
            print("没有优化结果可导出")
    
    def get_results(self):
        """
        Get optimization results.
        
        Returns:
            dict: Optimization results dictionary
        """
        return self.results.copy()

# SLOT: Main execution function - agent can customize
def main():
    """
    SLOT: Main execution function - agent can customize the execution flow.
    """
    # SLOT: This would typically be called with a loaded model
    # For template purposes, we'll create a placeholder
    print("Optimization template loaded successfully!")
    print("This template should be used with a loaded COBRA model.")

if __name__ == "__main__":
    main()
