"""
Main Template for Gene Deletion Analysis

This template provides a unified interface for the entire gene deletion analysis pipeline.
Agent systems can customize the entire workflow by modifying the configuration.
"""

import os
import sys
from datetime import datetime

# Import template components
from .model_loader_template import ModelLoaderTemplate
from .gene_analysis_template import GeneAnalysisTemplate
from .optimization_template import OptimizationTemplate
from .visualization_template import VisualizationTemplate
from .report_template import ReportTemplate

# Import configuration template
from .config_template import (
    MODEL_CONFIG,
    ANALYSIS_SCOPE,
    TARGET_PRODUCTS,
    OUTPUT_CONFIG
)

class GeneDeletionAnalysisTemplate:
    """
    Main template class for gene deletion analysis.
    Orchestrates the entire analysis pipeline with configurable slots.
    """
    
    def __init__(self, config_override=None):
        """
        Initialize the gene deletion analysis template.
        
        Args:
            config_override (dict): Optional configuration override
        """
        self.config_override = config_override or {}
        self.model = None
        self.model_info = None
        self.analysis_results = {}
        
        # Initialize template components
        self.model_loader = None
        self.gene_analyzer = None
        self.optimizer = None
        self.visualizer = None
        self.report_generator = None
        
        print("=== Gene Deletion Analysis Template Initialized ===")
        print(f"Model: {MODEL_CONFIG['model_name']}")
        print(f"Analysis Scope: {ANALYSIS_SCOPE['max_genes_to_analyze']} genes")
        print(f"Target Products: {len(TARGET_PRODUCTS)} products")
        print(f"Output Directory: {OUTPUT_CONFIG['output_directory']}")
    
    def run_complete_analysis(self):
        """
        SLOT: Run complete analysis pipeline - can be customized by agent.
        """
        print("\n=== 开始完整基因敲除分析流程 ===")
        
        try:
            # SLOT: Step 1 - Model Loading - agent can customize
            self._load_model()
            
            # SLOT: Step 2 - Gene Analysis - agent can customize
            self._perform_gene_analysis()
            
            # SLOT: Step 3 - Product Optimization - agent can customize
            self._perform_product_optimization()
            
            # SLOT: Step 4 - Visualization - agent can customize
            self._create_visualizations()
            
            # SLOT: Step 5 - Report Generation - agent can customize
            self._generate_reports()
            
            # SLOT: Step 6 - Additional Processing - agent can add
            self._perform_additional_processing()
            
            print("\n=== 分析流程完成 ===")
            return self.analysis_results
            
        except Exception as e:
            print(f"分析过程中出现错误: {e}")
            raise
    
    def _load_model(self):
        """
        SLOT: Load metabolic model - agent can customize.
        """
        print("\n--- 步骤 1: 模型加载 ---")
        
        # SLOT: Model loading configuration - agent can customize
        model_config_override = self.config_override.get('model_config', {})
        
        self.model_loader = ModelLoaderTemplate(model_config_override)
        self.model_loader.setup_visualization()
        self.model_loader.load_model()
        
        self.model = self.model_loader.get_model()
        self.model_info = self.model_loader.get_model_info()
        
        print("✓ 模型加载完成")
    
    def _perform_gene_analysis(self):
        """
        SLOT: Perform gene analysis - agent can customize.
        """
        print("\n--- 步骤 2: 基因分析 ---")
        
        # SLOT: Gene analysis configuration - agent can customize
        gene_config_override = self.config_override.get('gene_analysis_config', {})
        
        self.gene_analyzer = GeneAnalysisTemplate(self.model, gene_config_override)
        
        # SLOT: Gene selection - agent can customize
        self.gene_analyzer.select_genes_for_analysis()
        
        # SLOT: Knockout analysis - agent can customize
        knockout_results = self.gene_analyzer.analyze_single_gene_knockouts()
        self.analysis_results['knockout_analysis'] = knockout_results
        
        # SLOT: Product-specific knockout analysis - agent can customize
        if 'EX_succ_e' in TARGET_PRODUCTS:
            product_knockout_results = self.gene_analyzer.find_knockout_targets_for_product('EX_succ_e')
            self.analysis_results['product_knockout_results'] = product_knockout_results
        
        print("✓ 基因分析完成")
    
    def _perform_product_optimization(self):
        """
        SLOT: Perform product optimization - agent can customize.
        """
        print("\n--- 步骤 3: 产物优化分析 ---")
        
        # SLOT: Optimization configuration - agent can customize
        optimization_config_override = self.config_override.get('optimization_config', {})
        
        self.optimizer = OptimizationTemplate(self.model, optimization_config_override)
        
        # SLOT: Product optimization - agent can customize
        product_optimization_results = self.optimizer.analyze_product_optimization()
        self.analysis_results['product_optimization'] = product_optimization_results
        
        # SLOT: Additional optimization analysis - agent can add
        self._perform_additional_optimization()
        
        print("✓ 产物优化分析完成")
    
    def _perform_additional_optimization(self):
        """
        SLOT: Perform additional optimization - agent can implement.
        """
        # SLOT: Additional optimization logic - agent can add
        pass
    
    def _create_visualizations(self):
        """
        SLOT: Create visualizations - agent can customize.
        """
        print("\n--- 步骤 4: 可视化生成 ---")
        
        # SLOT: Visualization configuration - agent can customize
        visualization_config_override = self.config_override.get('visualization_config', {})
        
        self.visualizer = VisualizationTemplate(visualization_config_override)
        
        # SLOT: Comprehensive chart creation - agent can customize
        comprehensive_chart = self.visualizer.create_comprehensive_analysis_chart(self.analysis_results)
        
        if comprehensive_chart:
            self.analysis_results['comprehensive_chart'] = comprehensive_chart
        
        # SLOT: Additional visualizations - agent can add
        self._create_additional_visualizations()
        
        print("✓ 可视化生成完成")
    
    def _create_additional_visualizations(self):
        """
        SLOT: Create additional visualizations - agent can implement.
        """
        # SLOT: Additional visualization logic - agent can add
        pass
    
    def _generate_reports(self):
        """
        SLOT: Generate reports - agent can customize.
        """
        print("\n--- 步骤 5: 报告生成 ---")
        
        # SLOT: Report configuration - agent can customize
        report_config_override = self.config_override.get('report_config', {})
        
        self.report_generator = ReportTemplate(report_config_override)
        
        # SLOT: Comprehensive report generation - agent can customize
        comprehensive_report = self.report_generator.generate_comprehensive_report(
            self.analysis_results, 
            self.model_info
        )
        
        # SLOT: CRISPR guide generation - agent can customize
        if 'product_knockout_results' in self.analysis_results:
            top_genes = self._extract_top_genes()
            if top_genes:
                crispr_guide = self.report_generator.generate_crispr_guide(
                    top_genes, 
                    self.analysis_results
                )
        
        # SLOT: CSV and JSON results - agent can customize
        self.report_generator.generate_csv_results(self.analysis_results)
        self.report_generator.generate_json_results(self.analysis_results)
        
        # SLOT: Additional reports - agent can add
        self._generate_additional_reports()
        
        print("✓ 报告生成完成")
    
    def _extract_top_genes(self):
        """
        SLOT: Extract top genes for CRISPR guide - agent can customize.
        """
        # SLOT: Top gene extraction logic - agent can customize
        if 'product_knockout_results' in self.analysis_results:
            df = self.analysis_results['product_knockout_results']
            beneficial_knockouts = df[
                (df['viable']) & 
                (df['production_improvement'] > 5)
            ].sort_values('production_improvement', ascending=False)
            
            if not beneficial_knockouts.empty:
                return beneficial_knockouts['gene_id'].head(5).tolist()
        
        return []
    
    def _generate_additional_reports(self):
        """
        SLOT: Generate additional reports - agent can implement.
        """
        # SLOT: Additional report generation logic - agent can add
        pass
    
    def _perform_additional_processing(self):
        """
        SLOT: Perform additional processing - agent can implement.
        """
        # SLOT: Additional processing logic - agent can add
        pass
    
    def get_analysis_summary(self):
        """
        SLOT: Get analysis summary - agent can customize.
        """
        # SLOT: Summary generation logic - agent can customize
        summary = {
            'analysis_completed': True,
            'timestamp': datetime.now().isoformat(),
            'model_info': self.model_info,
            'results_available': list(self.analysis_results.keys()),
            'report_paths': self.report_generator.get_report_paths() if self.report_generator else {}
        }
        
        # SLOT: Additional summary information - agent can add
        if 'knockout_analysis' in self.analysis_results:
            df = self.analysis_results['knockout_analysis']
            summary['knockout_summary'] = {
                'total_genes_analyzed': len(df),
                'effect_distribution': df['effect_category'].value_counts().to_dict()
            }
        
        if 'product_optimization' in self.analysis_results:
            product_data = self.analysis_results['product_optimization']
            valid_products = {k: v for k, v in product_data.items() if v is not None}
            summary['product_summary'] = {
                'total_products_analyzed': len(product_data),
                'successful_optimizations': len(valid_products)
            }
        
        return summary
    
    def export_all_results(self, output_path=None):
        """
        SLOT: Export all results - agent can customize.
        """
        # SLOT: Export logic - agent can customize
        if output_path is None:
            output_path = os.path.join(OUTPUT_CONFIG['output_directory'], 'complete_analysis_results')
        
        os.makedirs(output_path, exist_ok=True)
        
        # Export analysis results
        import json
        import pickle
        
        # Export as JSON
        json_path = os.path.join(output_path, 'analysis_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Export as pickle (for Python objects)
        pickle_path = os.path.join(output_path, 'analysis_results.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(self.analysis_results, f)
        
        # Export summary
        summary = self.get_analysis_summary()
        summary_path = os.path.join(output_path, 'analysis_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 所有结果已导出到: {output_path}")
        return output_path
    
    def run_specific_analysis(self, analysis_type, **kwargs):
        """
        SLOT: Run specific analysis type - agent can customize.
        """
        # SLOT: Specific analysis logic - agent can customize
        if analysis_type == 'model_loading':
            return self._load_model()
        elif analysis_type == 'gene_analysis':
            return self._perform_gene_analysis()
        elif analysis_type == 'product_optimization':
            return self._perform_product_optimization()
        elif analysis_type == 'visualization':
            return self._create_visualizations()
        elif analysis_type == 'report_generation':
            return self._generate_reports()
        else:
            # SLOT: Custom analysis types - agent can implement
            return self._run_custom_analysis(analysis_type, **kwargs)
    
    def _run_custom_analysis(self, analysis_type, **kwargs):
        """
        SLOT: Run custom analysis - agent can implement.
        """
        # SLOT: Custom analysis implementation - agent can add
        raise NotImplementedError(f"Custom analysis type '{analysis_type}' not implemented")

# SLOT: Main execution function - agent can customize
def main():
    """
    SLOT: Main execution function - agent can customize the execution flow.
    """
    print("=== Gene Deletion Analysis Template ===")
    
    # SLOT: Configuration override - agent can provide custom config
    config_override = {
        # Example configuration overrides:
        # 'model_config': {'model_name': 'custom_model'},
        # 'gene_analysis_config': {'max_genes_to_analyze': 1000},
        # 'optimization_config': {'target_products': {'custom_product': 'Custom Product'}},
        # 'visualization_config': {'chart_types': {'product_comparison': True}},
        # 'report_config': {'generate_csv_results': True}
    }
    
    # SLOT: Initialize and run analysis - agent can customize
    analyzer = GeneDeletionAnalysisTemplate(config_override)
    
    # SLOT: Run complete analysis or specific components - agent can choose
    try:
        results = analyzer.run_complete_analysis()
        
        # SLOT: Get and display summary - agent can customize
        summary = analyzer.get_analysis_summary()
        print(f"\n分析摘要:")
        print(f"• 模型: {summary['model_info']['model_name']}")
        print(f"• 分析基因数: {summary['knockout_summary']['total_genes_analyzed']}")
        print(f"• 产物分析数: {summary['product_summary']['successful_optimizations']}")
        print(f"• 可用结果: {', '.join(summary['results_available'])}")
        
        # SLOT: Export results - agent can customize
        export_path = analyzer.export_all_results()
        print(f"• 结果导出路径: {export_path}")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        return None
    
    return results

if __name__ == "__main__":
    # SLOT: Standalone execution - agent can customize
    results = main()
    if results:
        print("\n=== 模板执行完成 ===")
    else:
        print("\n=== 模板执行失败 ===")
