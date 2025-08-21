"""
Visualization Template for Gene Deletion Analysis

This template provides configurable visualization functionality.
Agent systems can customize the visualization process by modifying the configuration.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Import configuration template
from .config_template import (
    PLOT_CONFIG,
    CHART_TYPES,
    OUTPUT_CONFIG
)

class VisualizationTemplate:
    """
    Template class for creating visualizations.
    Contains configurable slots for different chart types and styles.
    """
    
    def __init__(self, config_override=None):
        """
        Initialize the visualizer with optional configuration override.
        
        Args:
            config_override (dict): Optional configuration override
        """
        self.plot_config = PLOT_CONFIG.copy()
        self.chart_config = CHART_TYPES.copy()
        self.output_config = OUTPUT_CONFIG.copy()
        
        if config_override:
            self.plot_config.update(config_override.get('plot_config', {}))
            self.chart_config.update(config_override.get('chart_types', {}))
            self.output_config.update(config_override.get('output_config', {}))
        
        self.figures = {}
        self.setup_visualization()
    
    def setup_visualization(self):
        """
        SLOT: Setup visualization parameters - can be customized by agent.
        """
        # SLOT: Matplotlib configuration - agent can customize
        plt.rcParams['font.sans-serif'] = [self.plot_config['font_family'], 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # SLOT: Additional visualization setup - agent can add
        self._custom_visualization_setup()
    
    def _custom_visualization_setup(self):
        """
        SLOT: Custom visualization setup - agent can implement.
        """
        # SLOT: Custom visualization configuration - agent can add
        pass
    
    def create_comprehensive_analysis_chart(self, analysis_data):
        """
        SLOT: Create comprehensive analysis chart - can be customized by agent.
        """
        print("=== 创建综合分析图表 ===")
        
        # SLOT: Chart creation logic - agent can customize
        if not any(self.chart_config.values()):
            print("No chart types enabled in configuration")
            return None
        
        # SLOT: Figure setup - agent can customize
        fig, axes = self._setup_figure_layout()
        
        # SLOT: Chart generation - agent can customize
        chart_count = 0
        
        if self.chart_config['product_comparison']:
            self._create_product_comparison_chart(axes[chart_count // 2, chart_count % 2], analysis_data)
            chart_count += 1
        
        if self.chart_config['knockout_effects']:
            self._create_knockout_effects_chart(axes[chart_count // 2, chart_count % 2], analysis_data)
            chart_count += 1
        
        if self.chart_config['gene_targets']:
            self._create_gene_targets_chart(axes[chart_count // 2, chart_count % 2], analysis_data)
            chart_count += 1
        
        if self.chart_config['growth_production_tradeoff']:
            self._create_tradeoff_chart(axes[chart_count // 2, chart_count % 2], analysis_data)
            chart_count += 1
        
        # SLOT: Additional charts - agent can add
        self._create_custom_charts(axes, analysis_data)
        
        # SLOT: Figure finalization - agent can customize
        self._finalize_figure(fig)
        
        # SLOT: Save figure - agent can customize
        self._save_figure(fig, "comprehensive_analysis")
        
        self.figures['comprehensive_analysis'] = fig
        return fig
    
    def _setup_figure_layout(self):
        """
        SLOT: Setup figure layout - agent can customize.
        """
        # SLOT: Layout configuration - agent can customize
        figsize = self.plot_config['figure_size']
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('基因敲除优化策略分析', fontsize=16, fontweight='bold')
        
        return fig, axes
    
    def _create_product_comparison_chart(self, ax, analysis_data):
        """
        SLOT: Create product comparison chart - agent can customize.
        """
        # SLOT: Product comparison chart logic - agent can customize
        if 'product_optimization' not in analysis_data:
            ax.text(0.5, 0.5, 'No product data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('产物生产效率对比', fontweight='bold')
            return
        
        # SLOT: Data extraction - agent can customize
        products = []
        efficiencies = []
        
        for product_id, data in analysis_data['product_optimization'].items():
            if data is not None:
                products.append(data.get('product_name', product_id))
                efficiencies.append(data.get('production_efficiency', 0))
        
        if not products:
            ax.text(0.5, 0.5, 'No valid product data', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('产物生产效率对比', fontweight='bold')
            return
        
        # SLOT: Chart creation - agent can customize
        colors = plt.cm.Set3(np.linspace(0, 1, len(products)))
        bars = ax.bar(products, efficiencies, color=colors)
        
        ax.set_title('不同目标产物的生产效率对比', fontweight='bold')
        ax.set_ylabel('生产效率 (mmol/g/h)')
        ax.tick_params(axis='x', rotation=45)
        
        # SLOT: Value labels - agent can customize
        for bar, eff in zip(bars, efficiencies):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(efficiencies)*0.01, 
                   f'{eff:.1f}', ha='center', va='bottom', fontweight='bold')
    
    def _create_knockout_effects_chart(self, ax, analysis_data):
        """
        SLOT: Create knockout effects chart - agent can customize.
        """
        # SLOT: Knockout effects chart logic - agent can customize
        if 'knockout_analysis' not in analysis_data:
            ax.text(0.5, 0.5, 'No knockout data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('基因敲除效应分布', fontweight='bold')
            return
        
        # SLOT: Data extraction - agent can customize
        df = analysis_data['knockout_analysis']
        effect_counts = df['effect_category'].value_counts()
        
        if effect_counts.empty:
            ax.text(0.5, 0.5, 'No effect data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('基因敲除效应分布', fontweight='bold')
            return
        
        # SLOT: Chart creation - agent can customize
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#3498db', '#9b59b6']
        wedges, texts, autotexts = ax.pie(effect_counts.values, labels=effect_counts.index, 
                                         colors=colors[:len(effect_counts)], autopct='%1.1f%%', startangle=90)
        
        ax.set_title(f'基因敲除效应分布\n(基于{len(df)}个基因样本)', fontweight='bold')
    
    def _create_gene_targets_chart(self, ax, analysis_data):
        """
        SLOT: Create gene targets chart - agent can customize.
        """
        # SLOT: Gene targets chart logic - agent can customize
        if 'product_knockout_results' not in analysis_data:
            ax.text(0.5, 0.5, 'No gene target data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('最佳基因敲除目标', fontweight='bold')
            return
        
        # SLOT: Data extraction - agent can customize
        df = analysis_data['product_knockout_results']
        beneficial_knockouts = df[
            (df['viable']) & 
            (df['production_improvement'] > 5)
        ].sort_values('production_improvement', ascending=False).head(5)
        
        if beneficial_knockouts.empty:
            ax.text(0.5, 0.5, 'No beneficial targets found', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('最佳基因敲除目标', fontweight='bold')
            return
        
        # SLOT: Chart creation - agent can customize
        top_genes = beneficial_knockouts['gene_id'].tolist()
        improvements = beneficial_knockouts['production_improvement'].tolist()
        
        bars = ax.bar(range(len(top_genes)), improvements, color='#3498db')
        
        ax.set_title('最佳基因敲除目标', fontweight='bold')
        ax.set_ylabel('产量提升 (%)')
        ax.set_xlabel('基因ID')
        ax.set_xticks(range(len(top_genes)))
        ax.set_xticklabels(top_genes, rotation=45)
        
        # SLOT: Value labels - agent can customize
        for i, (bar, improvement) in enumerate(zip(bars, improvements)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   f'{improvement:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    def _create_tradeoff_chart(self, ax, analysis_data):
        """
        SLOT: Create growth-production tradeoff chart - agent can customize.
        """
        # SLOT: Tradeoff chart logic - agent can customize
        if 'product_knockout_results' not in analysis_data:
            ax.text(0.5, 0.5, 'No tradeoff data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('生长速率与产量权衡', fontweight='bold')
            return
        
        # SLOT: Data extraction - agent can customize
        df = analysis_data['product_knockout_results']
        viable_knockouts = df[df['viable']]
        
        if viable_knockouts.empty:
            ax.text(0.5, 0.5, 'No viable knockouts for tradeoff analysis', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('生长速率与产量权衡', fontweight='bold')
            return
        
        # SLOT: Chart creation - agent can customize
        growth_rates = viable_knockouts['growth'].tolist()
        production_rates = viable_knockouts['production'].tolist()
        gene_ids = viable_knockouts['gene_id'].tolist()
        
        scatter = ax.scatter(growth_rates, production_rates, c=range(len(growth_rates)), 
                           cmap='viridis', s=100, alpha=0.7)
        
        ax.set_xlabel('生长速率 (h⁻¹)')
        ax.set_ylabel('产物产量 (mmol/gDW/h)')
        ax.set_title('生长速率与产物产量权衡', fontweight='bold')
        
        # SLOT: Add labels for selected points - agent can customize
        for i, gene_id in enumerate(gene_ids[:3]):  # Label first 3 points
            ax.annotate(gene_id, (growth_rates[i], production_rates[i]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    def _create_custom_charts(self, axes, analysis_data):
        """
        SLOT: Create custom charts - agent can implement.
        """
        # SLOT: Custom chart creation logic - agent can add
        pass
    
    def _finalize_figure(self, fig):
        """
        SLOT: Finalize figure - agent can customize.
        """
        # SLOT: Figure finalization logic - agent can customize
        plt.tight_layout()
    
    def _save_figure(self, fig, chart_name):
        """
        SLOT: Save figure - agent can customize.
        """
        # SLOT: Save logic - agent can customize
        output_dir = self.output_config['output_directory']
        os.makedirs(output_dir, exist_ok=True)
        
        # SLOT: File naming - agent can customize
        if self.output_config['include_timestamp']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_config['file_prefix']}_{chart_name}_{timestamp}.{self.plot_config['save_format']}"
        else:
            filename = f"{self.output_config['file_prefix']}_{chart_name}.{self.plot_config['save_format']}"
        
        filepath = os.path.join(output_dir, filename)
        
        # SLOT: Save parameters - agent can customize
        fig.savefig(filepath, 
                   dpi=self.plot_config['dpi'], 
                   bbox_inches='tight', 
                   facecolor='white')
        
        print(f"✓ 图表已保存到: {filepath}")
        return filepath
    
    def create_single_chart(self, chart_type, data, title=None):
        """
        SLOT: Create single chart - agent can customize.
        """
        # SLOT: Single chart creation logic - agent can customize
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        if chart_type == 'product_comparison':
            self._create_product_comparison_chart(ax, {'product_optimization': data})
        elif chart_type == 'knockout_effects':
            self._create_knockout_effects_chart(ax, {'knockout_analysis': data})
        elif chart_type == 'gene_targets':
            self._create_gene_targets_chart(ax, {'product_knockout_results': data})
        elif chart_type == 'tradeoff':
            self._create_tradeoff_chart(ax, {'product_knockout_results': data})
        else:
            # SLOT: Custom chart type - agent can implement
            self._create_custom_single_chart(ax, chart_type, data)
        
        if title:
            ax.set_title(title, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def _create_custom_single_chart(self, ax, chart_type, data):
        """
        SLOT: Create custom single chart - agent can implement.
        """
        # SLOT: Custom single chart creation - agent can implement
        ax.text(0.5, 0.5, f'Custom chart: {chart_type}', ha='center', va='center', transform=ax.transAxes)
    
    def create_animation(self, data_sequence, chart_type='tradeoff'):
        """
        SLOT: Create animation - agent can implement.
        """
        # SLOT: Animation creation logic - agent can implement
        print("Animation creation not implemented in template")
        return None
    
    def export_chart_data(self, chart_name, data, format='csv'):
        """
        SLOT: Export chart data - agent can customize.
        """
        # SLOT: Data export logic - agent can customize
        output_dir = self.output_config['output_directory']
        os.makedirs(output_dir, exist_ok=True)
        
        if self.output_config['include_timestamp']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_config['file_prefix']}_{chart_name}_data_{timestamp}.{format}"
        else:
            filename = f"{self.output_config['file_prefix']}_{chart_name}_data.{format}"
        
        filepath = os.path.join(output_dir, filename)
        
        if format == 'csv':
            if isinstance(data, pd.DataFrame):
                data.to_csv(filepath, index=False, encoding='utf-8')
            else:
                pd.DataFrame(data).to_csv(filepath, index=False, encoding='utf-8')
        elif format == 'json':
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 图表数据已导出到: {filepath}")
        return filepath
    
    def get_figure(self, figure_name):
        """
        Get saved figure.
        
        Args:
            figure_name (str): Name of the figure
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        return self.figures.get(figure_name)
    
    def close_all_figures(self):
        """
        Close all figures to free memory.
        """
        plt.close('all')
        self.figures.clear()

# SLOT: Main execution function - agent can customize
def main():
    """
    SLOT: Main execution function - agent can customize the execution flow.
    """
    # SLOT: This would typically be called with analysis data
    # For template purposes, we'll create a placeholder
    print("Visualization template loaded successfully!")
    print("This template should be used with analysis data.")

if __name__ == "__main__":
    main()
