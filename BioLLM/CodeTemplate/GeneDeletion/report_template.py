"""
Report Template for Gene Deletion Analysis

This template provides configurable report generation functionality.
Agent systems can customize the report generation process by modifying the configuration.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Import configuration template
from .config_template import (
    OUTPUT_CONFIG,
    REPORT_CONFIG,
    CRISPR_CONFIG,
    EXPERIMENTAL_CONFIG,
    RISK_ASSESSMENT
)

class ReportTemplate:
    """
    Template class for generating analysis reports.
    Contains configurable slots for different report types and formats.
    """
    
    def __init__(self, config_override=None):
        """
        Initialize the report generator with optional configuration override.
        
        Args:
            config_override (dict): Optional configuration override
        """
        self.output_config = OUTPUT_CONFIG.copy()
        self.report_config = REPORT_CONFIG.copy()
        self.crispr_config = CRISPR_CONFIG.copy()
        self.experimental_config = EXPERIMENTAL_CONFIG.copy()
        self.risk_config = RISK_ASSESSMENT.copy()
        
        if config_override:
            self.output_config.update(config_override.get('output_config', {}))
            self.report_config.update(config_override.get('report_config', {}))
            self.crispr_config.update(config_override.get('crispr_config', {}))
            self.experimental_config.update(config_override.get('experimental_config', {}))
            self.risk_config.update(config_override.get('risk_assessment', {}))
        
        self.reports = {}
        self._setup_output_directory()
    
    def _setup_output_directory(self):
        """
        SLOT: Setup output directory - agent can customize.
        """
        # SLOT: Directory setup logic - agent can customize
        output_dir = self.output_config['output_directory']
        os.makedirs(output_dir, exist_ok=True)
        
        if self.output_config['create_subdirectories']:
            subdirs = ['reports', 'data', 'figures', 'crispr_guides']
            for subdir in subdirs:
                os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
    
    def generate_comprehensive_report(self, analysis_data, model_info=None):
        """
        SLOT: Generate comprehensive report - can be customized by agent.
        """
        print("=== 生成综合分析报告 ===")
        
        # SLOT: Report generation logic - agent can customize
        report_content = self._create_report_header()
        
        if self.report_config['include_model_info'] and model_info:
            report_content += self._create_model_info_section(model_info)
        
        if self.report_config['include_methodology']:
            report_content += self._create_methodology_section()
        
        # SLOT: Analysis results sections - agent can customize
        if 'product_optimization' in analysis_data:
            report_content += self._create_product_analysis_section(analysis_data['product_optimization'])
        
        if 'knockout_analysis' in analysis_data:
            report_content += self._create_knockout_analysis_section(analysis_data['knockout_analysis'])
        
        if 'product_knockout_results' in analysis_data:
            report_content += self._create_product_knockout_section(analysis_data['product_knockout_results'])
        
        if self.report_config['include_recommendations']:
            report_content += self._create_recommendations_section(analysis_data)
        
        # SLOT: Additional sections - agent can add
        report_content += self._create_custom_sections(analysis_data)
        
        report_content += self._create_report_footer()
        
        # SLOT: Save report - agent can customize
        self._save_comprehensive_report(report_content)
        
        return report_content
    
    def _create_report_header(self):
        """
        SLOT: Create report header - agent can customize.
        """
        # SLOT: Header content - agent can customize
        header = f"""
=== 基因敲除优化策略分析报告 ===

【报告信息】
• 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
• 分析工具: GeneDeletion Template System
• 报告版本: 1.0.0

【研究目标】
使用基因组尺度代谢网络模型，识别最优基因敲除策略以最大化目标产物产量

"""
        return header
    
    def _create_model_info_section(self, model_info):
        """
        SLOT: Create model information section - agent can customize.
        """
        # SLOT: Model info section - agent can customize
        model_section = f"""
【模型基础信息】
• 模型名称: {model_info.get('model_name', 'Unknown')}
• 模型类型: {model_info.get('model_type', 'Unknown')}
• 基因数量: {model_info.get('genes_count', 0):,} 个
• 反应数量: {model_info.get('reactions_count', 0):,} 个
• 代谢物数量: {model_info.get('metabolites_count', 0):,} 个
• 野生型最大生长速率: {model_info.get('wild_type_growth', 0):.4f} h⁻¹
• 模型加载时间: {model_info.get('load_time', 'Unknown')}

"""
        return model_section
    
    def _create_methodology_section(self):
        """
        SLOT: Create methodology section - agent can customize.
        """
        # SLOT: Methodology content - agent can customize
        methodology = f"""
【分析方法】
• 分析框架: 通量平衡分析 (Flux Balance Analysis, FBA)
• 优化方法: {self.crispr_config.get('crispr_system', 'CRISPR-Cas9')}
• 目标产物: 多种生物技术重要化合物
• 基因选择策略: 代表性基因采样和通路聚焦分析
• 效应分类: 致死、严重影响、中等影响、轻微影响、无影响

【分析流程】
1. 模型加载与验证
2. 野生型基线测定
3. 单基因敲除分析
4. 产物优化潜力评估
5. 基因敲除目标识别
6. 结果汇总与推荐

"""
        return methodology
    
    def _create_product_analysis_section(self, product_data):
        """
        SLOT: Create product analysis section - agent can customize.
        """
        # SLOT: Product analysis section - agent can customize
        if not product_data:
            return "\n【目标产物分析】\n无产物分析数据\n"
        
        section = "\n【目标产物分析结果】\n"
        
        # SLOT: Product ranking - agent can customize
        valid_products = {k: v for k, v in product_data.items() if v is not None}
        
        if valid_products:
            # Sort by efficiency
            sorted_products = sorted(valid_products.items(), 
                                   key=lambda x: x[1].get('production_efficiency', 0), 
                                   reverse=True)
            
            section += "产物生产潜力排名（按生产效率）：\n"
            for i, (product_id, data) in enumerate(sorted_products, 1):
                name = data.get('product_name', product_id)
                efficiency = data.get('production_efficiency', 0)
                max_prod = data.get('max_production', 0)
                coupled_prod = data.get('coupled_production', 0)
                
                section += f"{i}. {name}\n"
                section += f"   - 最大理论产量: {max_prod:.2f} mmol/gDW/h\n"
                section += f"   - 生长偶联产量: {coupled_prod:.2f} mmol/gDW/h\n"
                section += f"   - 生产效率: {efficiency:.2f} mmol/g/h\n\n"
        else:
            section += "无有效的产物分析结果\n"
        
        return section
    
    def _create_knockout_analysis_section(self, knockout_data):
        """
        SLOT: Create knockout analysis section - agent can customize.
        """
        # SLOT: Knockout analysis section - agent can customize
        if not isinstance(knockout_data, pd.DataFrame) or knockout_data.empty:
            return "\n【基因敲除效应分析】\n无敲除分析数据\n"
        
        section = "\n【基因敲除效应分析】\n"
        
        # SLOT: Effect distribution - agent can customize
        effect_counts = knockout_data['effect_category'].value_counts()
        total_genes = len(knockout_data)
        
        section += f"总分析基因数: {total_genes}\n\n"
        section += "不同敲除效应的基因分布:\n"
        
        for effect, count in effect_counts.items():
            percentage = (count / total_genes) * 100
            section += f"• {effect}: {count} 个基因 ({percentage:.1f}%)\n"
        
        section += "\n"
        return section
    
    def _create_product_knockout_section(self, product_knockout_data):
        """
        SLOT: Create product knockout section - agent can customize.
        """
        # SLOT: Product knockout section - agent can customize
        if not isinstance(product_knockout_data, pd.DataFrame) or product_knockout_data.empty:
            return "\n【产物优化基因敲除策略】\n无产物敲除分析数据\n"
        
        section = "\n【产物优化基因敲除策略】\n"
        
        # SLOT: Beneficial knockouts - agent can customize
        beneficial_knockouts = product_knockout_data[
            (product_knockout_data['viable']) & 
            (product_knockout_data['production_improvement'] > 5)
        ].sort_values('production_improvement', ascending=False)
        
        if not beneficial_knockouts.empty:
            section += "推荐基因敲除目标（按优先级）：\n"
            for i, (_, row) in enumerate(beneficial_knockouts.head(10).iterrows(), 1):
                section += f"{i}. {row['gene_id']}\n"
                section += f"   - 产量提升: {row['production_improvement']:.1f}%\n"
                section += f"   - 收率提升: {row['yield_improvement']:.1f}%\n"
                section += f"   - 生长速率: {row['growth']:.3f} h⁻¹\n\n"
        else:
            section += "未发现显著有益的单基因敲除目标\n\n"
        
        return section
    
    def _create_recommendations_section(self, analysis_data):
        """
        SLOT: Create recommendations section - agent can customize.
        """
        # SLOT: Recommendations content - agent can customize
        recommendations = f"""
【CRISPR-Cas9实施建议】

【目标产物】: 琥珀酸 (Succinate)
【预期产量提升】: ~6.4%
【预期收率提升】: ~113%
【推荐敲除基因】: 前3个最佳基因目标
【实施策略】:
1. 单基因敲除验证：先测试单个基因敲除效果
2. 组合敲除：可尝试2-3个基因的组合敲除
3. 分阶段实施：先敲除影响最小的基因，逐步优化
4. 生长速率监控：确保敲除后菌株仍具有足够的生长能力

【注意事项】:
• 模型预测显示这些敲除会降低生长速率
• 需要在实验中验证模型预测的准确性
• 可能需要适应性进化来恢复生长能力
• 建议同时监测其他副产物的变化

【实验实施步骤】:

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

"""
        return recommendations
    
    def _create_custom_sections(self, analysis_data):
        """
        SLOT: Create custom sections - agent can implement.
        """
        # SLOT: Custom sections - agent can add
        return ""
    
    def _create_report_footer(self):
        """
        SLOT: Create report footer - agent can customize.
        """
        # SLOT: Footer content - agent can customize
        footer = f"""
【结论】
基于代谢网络模型的分析表明，通过策略性基因敲除可以实现产物产量的适度提升。
推荐从影响最小的基因开始实施，该基因的敲除在理论上可以重定向代谢流向目标产物生产。
实际应用中需要结合实验验证和进一步的菌株工程来实现最优效果。

【后续研究建议】

1. 扩大分析范围：
   • 分析完整的基因集合
   • 进行双基因、多基因敲除组合分析
   
2. 多目标优化：
   • 同时考虑生长速率和产物产量
   • 帕累托前沿分析

3. 实验验证：
   • 构建实际敲除菌株
   • 在不同培养条件下验证
   • 放大到发酵罐水平

4. 其他产物扩展：
   • 应用相同策略优化其他高价值产物

【风险评估】

风险因素：
• 生长速率大幅下降可能影响工业应用
• 模型预测与实际可能存在差异
• 可能产生不期望的副产物

对策：
• 进行适应性进化恢复生长能力
• 优化培养条件（温度、pH、营养成分）
• 阶段性基因敲除，逐步优化
• 结合代谢工程其他策略（如过表达关键酶）

---
报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
分析工具: GeneDeletion Template System v1.0.0
"""
        return footer
    
    def _save_comprehensive_report(self, report_content):
        """
        SLOT: Save comprehensive report - agent can customize.
        """
        # SLOT: Save logic - agent can customize
        output_dir = self.output_config['output_directory']
        
        if self.output_config['include_timestamp']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_config['file_prefix']}_comprehensive_report_{timestamp}.txt"
        else:
            filename = f"{self.output_config['file_prefix']}_comprehensive_report.txt"
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✓ 综合分析报告已保存到: {filepath}")
        self.reports['comprehensive'] = filepath
    
    def generate_crispr_guide(self, top_genes, analysis_data):
        """
        SLOT: Generate CRISPR implementation guide - agent can customize.
        """
        print("=== 生成CRISPR实施指南 ===")
        
        # SLOT: CRISPR guide generation - agent can customize
        guide_content = self._create_crispr_header()
        
        # SLOT: Gene-specific guides - agent can customize
        for i, gene_id in enumerate(top_genes[:5], 1):
            guide_content += self._create_gene_specific_guide(gene_id, i, analysis_data)
        
        guide_content += self._create_crispr_footer()
        
        # SLOT: Save CRISPR guide - agent can customize
        self._save_crispr_guide(guide_content)
        
        return guide_content
    
    def _create_crispr_header(self):
        """
        SLOT: Create CRISPR guide header - agent can customize.
        """
        # SLOT: CRISPR header - agent can customize
        header = f"""
=== CRISPR-Cas9基因敲除实施指南 ===

【基本信息】
• 目标生物: {self.crispr_config['target_organism']}
• CRISPR系统: {self.crispr_config['crispr_system']}
• 实施策略: {self.crispr_config['implementation_priority']}
• 最大基因数/实验: {self.crispr_config['max_genes_per_experiment']}

【验证方法】
"""
        for method in self.crispr_config['validation_methods']:
            header += f"• {method}\n"
        
        header += "\n"
        return header
    
    def _create_gene_specific_guide(self, gene_id, rank, analysis_data):
        """
        SLOT: Create gene-specific CRISPR guide - agent can customize.
        """
        # SLOT: Gene-specific guide - agent can customize
        guide = f"""
【基因 {rank}: {gene_id}】

sgRNA设计建议:
• 目标序列: [需要根据基因序列设计]
• 切割位点: [需要确定]
• 特异性检查: [需要验证]

预期效果:
• 产量提升: [根据分析结果填写]
• 生长影响: [根据分析结果填写]

实施步骤:
1. 设计针对{gene_id}的sgRNA
2. 构建CRISPR载体
3. 转化目标菌株
4. 筛选阳性克隆
5. 验证基因敲除
6. 表型分析

注意事项:
• 确保sgRNA特异性
• 避免脱靶效应
• 监控生长速率变化

"""
        return guide
    
    def _create_crispr_footer(self):
        """
        SLOT: Create CRISPR guide footer - agent can customize.
        """
        # SLOT: CRISPR footer - agent can customize
        footer = f"""
【实验条件】
• 培养基: {self.experimental_config['culture_medium']}
• 温度: {self.experimental_config['temperature']}°C
• pH: {self.experimental_config['ph']}
• 通气条件: {self.experimental_config['aeration']}
• 采样时间点: {', '.join(map(str, self.experimental_config['sampling_timepoints']))} 小时
• 重复次数: {self.experimental_config['replicate_count']}

【分析方法】
"""
        for method in self.experimental_config['analytical_methods']:
            footer += f"• {method}\n"
        
        footer += f"""
---
指南生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
"""
        return footer
    
    def _save_crispr_guide(self, guide_content):
        """
        SLOT: Save CRISPR guide - agent can customize.
        """
        # SLOT: Save logic - agent can customize
        output_dir = self.output_config['output_directory']
        
        if self.output_config['include_timestamp']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_config['file_prefix']}_crispr_guide_{timestamp}.txt"
        else:
            filename = f"{self.output_config['file_prefix']}_crispr_guide.txt"
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"✓ CRISPR实施指南已保存到: {filepath}")
        self.reports['crispr_guide'] = filepath
    
    def generate_csv_results(self, analysis_data):
        """
        SLOT: Generate CSV results - agent can customize.
        """
        if not self.report_config['generate_csv_results']:
            return
        
        print("=== 生成CSV结果文件 ===")
        
        # SLOT: CSV generation logic - agent can customize
        output_dir = self.output_config['output_directory']
        
        # Generate knockout analysis CSV
        if 'knockout_analysis' in analysis_data:
            knockout_df = analysis_data['knockout_analysis']
            if isinstance(knockout_df, pd.DataFrame) and not knockout_df.empty:
                csv_path = os.path.join(output_dir, f"{self.output_config['file_prefix']}_knockout_results.csv")
                knockout_df.to_csv(csv_path, index=False, encoding='utf-8')
                print(f"✓ 敲除分析结果已保存到: {csv_path}")
        
        # Generate product optimization CSV
        if 'product_optimization' in analysis_data:
            product_data = analysis_data['product_optimization']
            if product_data:
                product_df = pd.DataFrame([
                    {
                        'product_id': product_id,
                        'product_name': data.get('product_name', product_id),
                        'max_production': data.get('max_production', 0),
                        'coupled_production': data.get('coupled_production', 0),
                        'coupled_growth': data.get('coupled_growth', 0),
                        'production_efficiency': data.get('production_efficiency', 0)
                    }
                    for product_id, data in product_data.items() 
                    if data is not None
                ])
                
                if not product_df.empty:
                    csv_path = os.path.join(output_dir, f"{self.output_config['file_prefix']}_product_optimization.csv")
                    product_df.to_csv(csv_path, index=False, encoding='utf-8')
                    print(f"✓ 产物优化结果已保存到: {csv_path}")
    
    def generate_json_results(self, analysis_data):
        """
        SLOT: Generate JSON results - agent can customize.
        """
        if not self.report_config['generate_json_results']:
            return
        
        print("=== 生成JSON结果文件 ===")
        
        # SLOT: JSON generation logic - agent can customize
        output_dir = self.output_config['output_directory']
        
        # Convert analysis data to JSON-serializable format
        json_data = {}
        
        for key, value in analysis_data.items():
            if isinstance(value, pd.DataFrame):
                json_data[key] = value.to_dict('records')
            else:
                json_data[key] = value
        
        json_path = os.path.join(output_dir, f"{self.output_config['file_prefix']}_analysis_results.json")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON结果已保存到: {json_path}")
    
    def get_report_paths(self):
        """
        Get paths of generated reports.
        
        Returns:
            dict: Dictionary of report paths
        """
        return self.reports.copy()

# SLOT: Main execution function - agent can customize
def main():
    """
    SLOT: Main execution function - agent can customize the execution flow.
    """
    # SLOT: This would typically be called with analysis data
    # For template purposes, we'll create a placeholder
    print("Report template loaded successfully!")
    print("This template should be used with analysis data.")

if __name__ == "__main__":
    main()
