"""
Gene Analysis Template for Gene Deletion Analysis

This template provides configurable gene knockout analysis functionality.
Agent systems can customize the analysis process by modifying the configuration.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import warnings

# Import configuration template
from .config_template import (
    ANALYSIS_SCOPE, 
    KNOCKOUT_EFFECT_CLASSIFICATION, 
    CANDIDATE_GENE_CRITERIA,
    TARGET_PRODUCTS
)

warnings.filterwarnings('ignore')

class GeneAnalysisTemplate:
    """
    Template class for gene knockout analysis.
    Contains configurable slots for different analysis strategies.
    """
    
    def __init__(self, model, config_override=None):
        """
        Initialize the gene analyzer with a metabolic model.
        
        Args:
            model: COBRA metabolic model
            config_override (dict): Optional configuration override
        """
        self.model = model
        self.analysis_config = ANALYSIS_SCOPE.copy()
        self.effect_config = KNOCKOUT_EFFECT_CLASSIFICATION.copy()
        self.candidate_config = CANDIDATE_GENE_CRITERIA.copy()
        
        if config_override:
            self.analysis_config.update(config_override.get('analysis_scope', {}))
            self.effect_config.update(config_override.get('effect_classification', {}))
            self.candidate_config.update(config_override.get('candidate_criteria', {}))
        
        self.results = {}
        self.gene_list = []
        
    def select_genes_for_analysis(self):
        """
        SLOT: Select genes for analysis - can be customized by agent.
        """
        print("=== 基因选择策略 ===")
        
        # SLOT: Gene selection strategy - agent can customize
        strategy = self.analysis_config['gene_selection_strategy']
        
        if strategy == 'representative':
            self.gene_list = self._select_representative_genes()
        elif strategy == 'pathway_focused':
            self.gene_list = self._select_pathway_genes()
        elif strategy == 'all_genes':
            self.gene_list = self._select_all_genes()
        elif strategy == 'custom':
            self.gene_list = self._select_custom_genes()
        else:
            raise ValueError(f"Unknown gene selection strategy: {strategy}")
        
        # SLOT: Apply gene filtering - agent can customize
        self._apply_gene_filters()
        
        print(f"已选择 {len(self.gene_list)} 个基因进行分析")
        return self.gene_list
    
    def _select_representative_genes(self):
        """
        SLOT: Select representative genes - agent can customize.
        """
        # SLOT: Representative gene selection logic - agent can customize
        all_genes = [gene.id for gene in self.model.genes]
        max_genes = self.analysis_config['max_genes_to_analyze']
        
        if len(all_genes) <= max_genes:
            return all_genes
        else:
            # SLOT: Sampling strategy - agent can customize
            step = len(all_genes) // max_genes
            return all_genes[::step][:max_genes]
    
    def _select_pathway_genes(self):
        """
        SLOT: Select pathway-focused genes - agent can customize.
        """
        # SLOT: Pathway-focused gene selection - agent can customize
        pathway_genes = []
        keywords = self.candidate_config['pathway_keywords']
        
        for rxn in self.model.reactions:
            if any(keyword in rxn.id.lower() for keyword in keywords):
                pathway_genes.extend([gene.id for gene in rxn.genes])
        
        # SLOT: Deduplication and limiting - agent can customize
        pathway_genes = list(set(pathway_genes))
        max_candidates = self.candidate_config['max_candidates']
        
        return pathway_genes[:max_candidates]
    
    def _select_all_genes(self):
        """
        SLOT: Select all genes - agent can customize.
        """
        # SLOT: All gene selection logic - agent can customize
        return [gene.id for gene in self.model.genes]
    
    def _select_custom_genes(self):
        """
        SLOT: Select custom genes - agent can implement.
        """
        # SLOT: Custom gene selection logic - agent can implement
        raise NotImplementedError("Custom gene selection not implemented")
    
    def _apply_gene_filters(self):
        """
        SLOT: Apply gene filters - agent can customize.
        """
        # SLOT: Gene filtering logic - agent can customize
        if self.analysis_config['exclude_essential_genes']:
            self._filter_essential_genes()
        
        # SLOT: Additional filtering - agent can add
        self._custom_gene_filtering()
    
    def _filter_essential_genes(self):
        """
        SLOT: Filter essential genes - agent can customize.
        """
        # SLOT: Essential gene filtering logic - agent can customize
        # This is a placeholder - agent can implement actual essential gene detection
        pass
    
    def _custom_gene_filtering(self):
        """
        SLOT: Custom gene filtering - agent can implement.
        """
        # SLOT: Custom filtering logic - agent can add
        pass
    
    def analyze_single_gene_knockouts(self):
        """
        SLOT: Analyze single gene knockouts - can be customized by agent.
        """
        print("=== 基因敲除分析策略框架 ===")
        
        if not self.gene_list:
            self.select_genes_for_analysis()
        
        # SLOT: Get wild type baseline - agent can customize
        wild_type_growth = self._get_wild_type_growth()
        
        print(f"野生型生长速率: {wild_type_growth:.4f}")
        print(f"开始分析 {len(self.gene_list)} 个基因的敲除效应...")
        
        results = []
        
        for i, gene_id in enumerate(self.gene_list):
            # SLOT: Progress reporting - agent can customize
            if i % 200 == 0:
                print(f"  已完成: {i}/{len(self.gene_list)} ({i/len(self.gene_list)*100:.1f}%)")
            
            # SLOT: Gene knockout analysis - agent can customize
            result = self._analyze_single_gene(gene_id, wild_type_growth)
            results.append(result)
        
        # SLOT: Results processing - agent can customize
        self.results['knockout_analysis'] = pd.DataFrame(results)
        self._process_knockout_results()
        
        return self.results['knockout_analysis']
    
    def _get_wild_type_growth(self):
        """
        SLOT: Get wild type growth rate - agent can customize.
        """
        # SLOT: Wild type growth calculation - agent can customize
        solution = self.model.optimize()
        return solution.objective_value if solution.status == 'optimal' else 0
    
    def _analyze_single_gene(self, gene_id, wild_type_growth):
        """
        SLOT: Analyze single gene knockout - agent can customize.
        """
        try:
            # SLOT: Gene knockout implementation - agent can customize
            with self.model:
                gene = self.model.genes.get_by_id(gene_id)
                gene.knock_out()
                solution = self.model.optimize()
                
                # SLOT: Growth rate calculation - agent can customize
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                growth_ratio = growth_rate / wild_type_growth if wild_type_growth > 0 else 0
                
                # SLOT: Effect classification - agent can customize
                effect = self._classify_knockout_effect(growth_rate, growth_ratio)
                
                # SLOT: Additional analysis - agent can customize
                additional_info = self._get_additional_gene_info(gene_id)
                
                return {
                    'gene_id': gene_id,
                    'growth_rate': growth_rate,
                    'growth_ratio': growth_ratio,
                    'growth_reduction': (1 - growth_ratio) * 100,
                    'effect_category': effect,
                    'reactions_affected': len([rxn for rxn in gene.reactions]),
                    **additional_info
                }
        
        except Exception as e:
            # SLOT: Error handling - agent can customize
            return self._handle_gene_analysis_error(gene_id, e)
    
    def _classify_knockout_effect(self, growth_rate, growth_ratio):
        """
        SLOT: Classify knockout effect - agent can customize.
        """
        # SLOT: Effect classification logic - agent can customize
        lethal_threshold = self.effect_config['lethal_threshold']
        severe_threshold = self.effect_config['severe_effect_threshold']
        moderate_threshold = self.effect_config['moderate_effect_threshold']
        mild_threshold = self.effect_config['mild_effect_threshold']
        
        if growth_rate < lethal_threshold:
            return "致死"
        elif growth_rate < severe_threshold:
            return "严重影响"
        elif growth_ratio < moderate_threshold:
            return "中等影响"
        elif growth_ratio < mild_threshold:
            return "轻微影响"
        else:
            return "无影响"
    
    def _get_additional_gene_info(self, gene_id):
        """
        SLOT: Get additional gene information - agent can implement.
        """
        # SLOT: Additional gene information extraction - agent can add
        return {}
    
    def _handle_gene_analysis_error(self, gene_id, error):
        """
        SLOT: Handle gene analysis error - agent can customize.
        """
        # SLOT: Error handling logic - agent can customize
        return {
            'gene_id': gene_id,
            'growth_rate': 0,
            'growth_ratio': 0,
            'growth_reduction': 100,
            'effect_category': "分析错误",
            'reactions_affected': 0,
            'error_message': str(error)
        }
    
    def _process_knockout_results(self):
        """
        SLOT: Process knockout results - agent can customize.
        """
        print(f"\n=== 基因敲除分析结果汇总 ===")
        
        df = self.results['knockout_analysis']
        print(f"总分析基因数: {len(df)}")
        
        # SLOT: Effect distribution analysis - agent can customize
        effect_counts = df['effect_category'].value_counts()
        print(f"\n不同敲除效应的基因分布:")
        
        for effect, count in effect_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {effect}: {count} 个基因 ({percentage:.1f}%)")
        
        # SLOT: Additional result processing - agent can add
        self._custom_result_processing()
    
    def _custom_result_processing(self):
        """
        SLOT: Custom result processing - agent can implement.
        """
        # SLOT: Custom processing logic - agent can add
        pass
    
    def find_knockout_targets_for_product(self, target_product_id):
        """
        SLOT: Find knockout targets for specific product - agent can customize.
        """
        print(f"=== {TARGET_PRODUCTS.get(target_product_id, {}).get('name', target_product_id)}生产基因敲除优化策略 ===")
        
        # SLOT: Candidate gene selection for product optimization - agent can customize
        candidate_genes = self._select_product_candidate_genes(target_product_id)
        
        print(f"分析 {len(candidate_genes)} 个候选基因对产物生产的影响...")
        
        # SLOT: Get wild type baseline for product - agent can customize
        wt_production, wt_growth = self._get_wild_type_product_baseline(target_product_id)
        
        print(f"野生型产物产量: {wt_production:.4f} mmol/gDW/h")
        print(f"野生型生长速率: {wt_growth:.4f} h⁻¹")
        
        # SLOT: Product optimization analysis - agent can customize
        knockout_results = self._analyze_product_knockouts(candidate_genes, target_product_id, wt_production, wt_growth)
        
        # SLOT: Process product optimization results - agent can customize
        self._process_product_results(knockout_results, target_product_id)
        
        return knockout_results
    
    def _select_product_candidate_genes(self, target_product_id):
        """
        SLOT: Select candidate genes for product optimization - agent can customize.
        """
        # SLOT: Product-specific gene selection - agent can customize
        central_metabolism_genes = []
        keywords = self.candidate_config['pathway_keywords']
        
        for rxn in self.model.reactions:
            if any(pathway in rxn.id.lower() for pathway in keywords):
                central_metabolism_genes.extend([gene.id for gene in rxn.genes])
        
        candidate_genes = list(set(central_metabolism_genes))[:self.candidate_config['max_candidates']]
        return candidate_genes
    
    def _find_biomass_reaction(self):
        """
        SLOT: Find biomass reaction - agent can customize.
        """
        # SLOT: Biomass reaction detection - agent can customize
        biomass_keywords = ['BIOMASS', 'biomass', 'Biomass']
        
        for reaction in self.model.reactions:
            if any(keyword in reaction.id for keyword in biomass_keywords):
                return reaction
        
        # If no biomass reaction found, return the first reaction (fallback)
        if len(self.model.reactions) > 0:
            return self.model.reactions[0]
        
        return None

    def _get_wild_type_product_baseline(self, target_product_id):
        """
        SLOT: Get wild type product baseline - agent can customize.
        """
        # SLOT: Wild type product baseline calculation - agent can customize
        with self.model:
            if target_product_id in [rxn.id for rxn in self.model.reactions]:
                self.model.objective = target_product_id
                
                # Find biomass reaction dynamically
                biomass_reaction = self._find_biomass_reaction()
                if biomass_reaction is None:
                    print("  警告: 未找到生物量反应，使用默认设置")
                    return 0, 0
                
                biomass_constraint = biomass_reaction
                biomass_constraint.lower_bound = 0.1
                
                wt_solution = self.model.optimize()
                wt_production = wt_solution.objective_value if wt_solution.status == 'optimal' else 0
                wt_growth = wt_solution.fluxes[biomass_reaction.id] if wt_solution.status == 'optimal' else 0
                
                return wt_production, wt_growth
        
        return 0, 0
    
    def _analyze_product_knockouts(self, candidate_genes, target_product_id, wt_production, wt_growth):
        """
        SLOT: Analyze product knockouts - agent can customize.
        """
        knockout_results = []
        
        for i, gene_id in enumerate(candidate_genes):
            # SLOT: Progress reporting - agent can customize
            if i % 20 == 0:
                print(f"  进度: {i}/{len(candidate_genes)} ({i/len(candidate_genes)*100:.1f}%)")
            
            # SLOT: Product knockout analysis - agent can customize
            result = self._analyze_single_product_knockout(gene_id, target_product_id, wt_production, wt_growth)
            knockout_results.append(result)
        
        return pd.DataFrame(knockout_results)
    
    def _analyze_single_product_knockout(self, gene_id, target_product_id, wt_production, wt_growth):
        """
        SLOT: Analyze single product knockout - agent can customize.
        """
        try:
            with self.model:
                # SLOT: Gene knockout - agent can customize
                gene = self.model.genes.get_by_id(gene_id)
                gene.knock_out()
                
                # SLOT: Product optimization setup - agent can customize
                self.model.objective = target_product_id
                
                # Find biomass reaction dynamically
                biomass_reaction = self._find_biomass_reaction()
                if biomass_reaction is None:
                    print(f"  警告: 基因 {gene_id} 分析中未找到生物量反应")
                    return self._handle_product_knockout_error(gene_id)
                
                biomass_constraint = biomass_reaction
                biomass_constraint.lower_bound = 0.05
                
                solution = self.model.optimize()
                
                if solution.status == 'optimal':
                    production = solution.objective_value
                    growth = solution.fluxes[biomass_reaction.id]
                    
                    # SLOT: Improvement calculation - agent can customize
                    production_improvement = ((production - wt_production) / wt_production) * 100 if wt_production > 0 else 0
                    yield_improvement = (production / growth - wt_production / wt_growth) / (wt_production / wt_growth) * 100 if wt_growth > 0 and growth > 0 else 0
                    
                    return {
                        'gene_id': gene_id,
                        'production': production,
                        'growth': growth,
                        'production_improvement': production_improvement,
                        'yield': production / growth if growth > 0 else 0,
                        'yield_improvement': yield_improvement,
                        'viable': growth >= 0.05
                    }
                else:
                    return self._handle_product_knockout_error(gene_id)
                    
        except Exception as e:
            print(f"  基因 {gene_id} 分析错误: {e}")
            return self._handle_product_knockout_error(gene_id)
    
    def _handle_product_knockout_error(self, gene_id):
        """
        SLOT: Handle product knockout error - agent can customize.
        """
        # SLOT: Error handling for product knockouts - agent can customize
        return {
            'gene_id': gene_id,
            'production': 0,
            'growth': 0,
            'production_improvement': -100,
            'yield': 0,
            'yield_improvement': -100,
            'viable': False
        }
    
    def _process_product_results(self, knockout_df, target_product_id):
        """
        SLOT: Process product results - agent can customize.
        """
        print(f"\n=== 基因敲除分析结果 ===")
        print(f"有效敲除目标: {len(knockout_df[knockout_df['viable']])} / {len(knockout_df)}")
        
        # SLOT: Beneficial knockout identification - agent can customize
        beneficial_knockouts = knockout_df[
            (knockout_df['viable']) & 
            (knockout_df['production_improvement'] > 5)
        ].sort_values('production_improvement', ascending=False)
        
        print(f"\n=== 前10个最佳基因敲除目标 ===")
        if len(beneficial_knockouts) > 0:
            top_targets = beneficial_knockouts.head(10)[['gene_id', 'production', 'growth', 'production_improvement', 'yield_improvement']]
            print(top_targets.round(4).to_string(index=False))
        else:
            print("未发现显著有益的单基因敲除目标")
            
            # SLOT: Alternative target identification - agent can customize
            self._identify_alternative_targets(knockout_df)
    
    def _identify_alternative_targets(self, knockout_df):
        """
        SLOT: Identify alternative targets - agent can customize.
        """
        # SLOT: Alternative target identification logic - agent can customize
        moderate_targets = knockout_df[
            (knockout_df['viable']) & 
            (knockout_df['production_improvement'] > -10)
        ].sort_values('production_improvement', ascending=False).head(10)
        
        print(f"\n=== 影响较小的敲除目标（参考） ===")
        if len(moderate_targets) > 0:
            print(moderate_targets[['gene_id', 'production', 'growth', 'production_improvement', 'yield_improvement']].round(4).to_string(index=False))
    
    def get_results(self):
        """
        Get analysis results.
        
        Returns:
            dict: Analysis results dictionary
        """
        return self.results.copy()

# SLOT: Main execution function - agent can customize
def main():
    """
    SLOT: Main execution function - agent can customize the execution flow.
    """
    # SLOT: This would typically be called with a loaded model
    # For template purposes, we'll create a placeholder
    print("Gene analysis template loaded successfully!")
    print("This template should be used with a loaded COBRA model.")

if __name__ == "__main__":
    main()
