#!/usr/bin/env python3
"""
Gene Deletion Analysis Agent - Analyzes gene deletion analysis results and provides LLM insights
"""

import os
import json
import traceback
from typing import Dict, Any, List, Optional
from pathlib import Path

class GeneDeletionAnalysisAgent:
    """
    Agent for analyzing gene deletion analysis results and providing LLM insights
    """
    
    def __init__(self):
        """Initialize the gene deletion analysis agent"""
        self.analysis_results = {}
        self.current_model = None
    
    def load_analysis_results(self, model_name: str) -> bool:
        """
        Load analysis results for a specific model
        
        Args:
            model_name (str): Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from experiment_executor import get_analysis_status
            
            analysis_data = get_analysis_status(model_name)
            if analysis_data:
                self.analysis_results = analysis_data
                self.current_model = model_name
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error loading analysis results: {e}")
            return False
    
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze the loaded results and provide insights
        
        Returns:
            Dict containing analysis insights
        """
        if not self.analysis_results:
            return {
                'success': False,
                'error': 'No analysis results loaded'
            }
        
        try:
            insights = {
                'success': True,
                'model_name': self.current_model,
                'analysis_summary': {},
                'key_findings': [],
                'recommendations': [],
                'visualization_summary': {},
                'report_summary': {}
            }
            
            # Extract analysis summary
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                insights['analysis_summary'] = {
                    'total_genes_analyzed': summary.get('knockout_summary', {}).get('total_genes_analyzed', 0),
                    'effect_distribution': summary.get('knockout_summary', {}).get('effect_distribution', {}),
                    'successful_optimizations': summary.get('product_summary', {}).get('successful_optimizations', 0),
                    'top_product': summary.get('product_summary', {}).get('top_product', {})
                }
            
            # Generate key findings
            insights['key_findings'] = self._generate_key_findings()
            
            # Generate recommendations
            insights['recommendations'] = self._generate_recommendations()
            
            # Summarize visualizations
            insights['visualization_summary'] = self._summarize_visualizations()
            
            # Summarize reports
            insights['report_summary'] = self._summarize_reports()
            
            return insights
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analyzing results: {e}',
                'traceback': traceback.format_exc()
            }
    
    def _generate_key_findings(self) -> List[str]:
        """Generate key findings from the analysis results"""
        findings = []
        
        try:
            # Analyze gene knockout effects
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                knockout_summary = summary.get('knockout_summary', {})
                
                total_genes = knockout_summary.get('total_genes_analyzed', 0)
                effect_dist = knockout_summary.get('effect_distribution', {})
                
                if total_genes > 0:
                    findings.append(f"📊 Analyzed {total_genes} genes for knockout effects")
                    
                    # Analyze effect distribution
                    lethal_count = effect_dist.get('致死', 0)
                    severe_count = effect_dist.get('严重影响', 0)
                    moderate_count = effect_dist.get('中等影响', 0)
                    mild_count = effect_dist.get('轻微影响', 0)
                    no_effect_count = effect_dist.get('无影响', 0)
                    
                    if lethal_count > 0:
                        lethal_percent = (lethal_count / total_genes) * 100
                        findings.append(f"⚠️ {lethal_count} genes ({lethal_percent:.1f}%) are lethal when knocked out")
                    
                    if no_effect_count > 0:
                        no_effect_percent = (no_effect_count / total_genes) * 100
                        findings.append(f"✅ {no_effect_count} genes ({no_effect_percent:.1f}%) show no effect when knocked out")
                    
                    if moderate_count > 0 or mild_count > 0:
                        potential_targets = moderate_count + mild_count
                        potential_percent = (potential_targets / total_genes) * 100
                        findings.append(f"🎯 {potential_targets} genes ({potential_percent:.1f}%) show moderate to mild effects - potential targets for optimization")
            
            # Analyze product optimization results
            if 'results' in self.analysis_results:
                results = self.analysis_results['results']
                product_optimization = results.get('product_optimization', {})
                
                if product_optimization:
                    valid_products = {k: v for k, v in product_optimization.items() if v is not None}
                    findings.append(f"🧪 Analyzed {len(valid_products)} target products for optimization potential")
                    
                    # Find top performing products
                    if valid_products:
                        top_product = max(valid_products.items(), 
                                        key=lambda x: x[1].get('production_efficiency', 0))
                        top_name = top_product[1].get('product_name', top_product[0])
                        top_efficiency = top_product[1].get('production_efficiency', 0)
                        findings.append(f"🏆 {top_name} shows highest production efficiency: {top_efficiency:.2f} mmol/g/h")
            
            # Analyze gene knockout targets
            if 'results' in self.analysis_results:
                results = self.analysis_results['results']
                product_knockout_results = results.get('product_knockout_results')
                
                if product_knockout_results is not None and not product_knockout_results.empty:
                    beneficial_knockouts = product_knockout_results[
                        (product_knockout_results['viable']) & 
                        (product_knockout_results['production_improvement'] > 5)
                    ]
                    
                    if not beneficial_knockouts.empty:
                        top_improvement = beneficial_knockouts['production_improvement'].max()
                        findings.append(f"🚀 Best gene knockout shows {top_improvement:.1f}% production improvement")
                        
                        viable_count = len(product_knockout_results[product_knockout_results['viable']])
                        findings.append(f"🔬 {viable_count} gene knockouts maintain cell viability")
            
        except Exception as e:
            findings.append(f"❌ Error generating findings: {e}")
        
        return findings
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        try:
            # General recommendations
            recommendations.append("🔬 **Experimental Validation**: All computational predictions should be validated experimentally")
            recommendations.append("📊 **Comprehensive Testing**: Test multiple gene combinations for synergistic effects")
            recommendations.append("⚖️ **Growth-Production Balance**: Monitor growth rates when implementing gene knockouts")
            
            # Specific recommendations based on results
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                knockout_summary = summary.get('knockout_summary', {})
                effect_dist = knockout_summary.get('effect_distribution', {})
                
                lethal_count = effect_dist.get('致死', 0)
                if lethal_count > 0:
                    recommendations.append("⚠️ **Avoid Lethal Genes**: Focus on non-lethal gene knockouts for viable strains")
                
                no_effect_count = effect_dist.get('无影响', 0)
                if no_effect_count > 0:
                    recommendations.append("🎯 **Target Non-Essential Genes**: Prioritize genes with minimal growth impact")
            
            # Product-specific recommendations
            if 'results' in self.analysis_results:
                results = self.analysis_results['results']
                product_optimization = results.get('product_optimization', {})
                
                if product_optimization:
                    valid_products = {k: v for k, v in product_optimization.items() if v is not None}
                    if valid_products:
                        recommendations.append("🏭 **Scale-Up Strategy**: Develop fermentation protocols for high-yield products")
                        recommendations.append("🔧 **Metabolic Engineering**: Consider overexpression of key enzymes in addition to knockouts")
            
            # CRISPR implementation recommendations
            recommendations.append("🧬 **CRISPR Implementation**: Use validated sgRNA designs and proper controls")
            recommendations.append("📈 **Progressive Optimization**: Implement knockouts stepwise to monitor effects")
            recommendations.append("🔄 **Adaptive Evolution**: Consider adaptive evolution to improve strain performance")
            
        except Exception as e:
            recommendations.append(f"❌ Error generating recommendations: {e}")
        
        return recommendations
    
    def _summarize_visualizations(self) -> Dict[str, Any]:
        """Summarize visualization files"""
        summary = {
            'total_files': 0,
            'image_files': 0,
            'html_files': 0,
            'file_list': []
        }
        
        try:
            if 'visualizations' in self.analysis_results:
                visualizations = self.analysis_results['visualizations']
                summary['total_files'] = len(visualizations)
                
                for viz in visualizations:
                    summary['file_list'].append({
                        'name': viz.get('name', 'Unknown'),
                        'type': viz.get('type', 'Unknown'),
                        'size': viz.get('size', 0)
                    })
                    
                    if viz.get('type') == 'image':
                        summary['image_files'] += 1
                    elif viz.get('type') == 'html':
                        summary['html_files'] += 1
                        
        except Exception as e:
            summary['error'] = str(e)
        
        return summary
    
    def _summarize_reports(self) -> Dict[str, Any]:
        """Summarize report files"""
        summary = {
            'total_reports': 0,
            'report_types': [],
            'report_list': []
        }
        
        try:
            if 'report_paths' in self.analysis_results:
                report_paths = self.analysis_results['report_paths']
                summary['total_reports'] = len(report_paths)
                summary['report_types'] = list(report_paths.keys())
                
                for report_type, report_path in report_paths.items():
                    if os.path.exists(report_path):
                        summary['report_list'].append({
                            'type': report_type,
                            'path': report_path,
                            'name': os.path.basename(report_path),
                            'size': os.path.getsize(report_path)
                        })
                        
        except Exception as e:
            summary['error'] = str(e)
        
        return summary
    
    def generate_llm_response(self, user_question: str = None) -> str:
        """
        Generate a comprehensive LLM response based on analysis results
        
        Args:
            user_question (str): Optional user question to focus the response
            
        Returns:
            str: Comprehensive LLM response
        """
        if not self.analysis_results:
            return "❌ No analysis results available. Please run gene deletion analysis first."
        
        try:
            # Analyze the results
            insights = self.analyze_results()
            
            if not insights['success']:
                return f"❌ Error analyzing results: {insights.get('error', 'Unknown error')}"
            
            # Generate comprehensive response
            response = f"""
# 🧬 Gene Deletion Analysis Report for {self.current_model}

## 📊 Analysis Overview

This comprehensive gene deletion analysis was performed on the **{self.current_model}** metabolic model to identify optimal gene knockout strategies for improving target product production.

### 🔬 Analysis Scope
- **Total Genes Analyzed**: {insights['analysis_summary'].get('total_genes_analyzed', 0)}
- **Target Products**: {insights['analysis_summary'].get('successful_optimizations', 0)} products analyzed
- **Analysis Method**: Flux Balance Analysis (FBA) with gene knockout simulation

## 🎯 Key Findings

"""
            
            # Add key findings
            for finding in insights['key_findings']:
                response += f"{finding}\n\n"
            
            # Add effect distribution if available
            effect_dist = insights['analysis_summary'].get('effect_distribution', {})
            if effect_dist:
                response += "### 📈 Gene Knockout Effect Distribution\n\n"
                for effect, count in effect_dist.items():
                    total = insights['analysis_summary'].get('total_genes_analyzed', 0)
                    if total > 0:
                        percentage = (count / total) * 100
                        response += f"- **{effect}**: {count} genes ({percentage:.1f}%)\n"
                response += "\n"
            
            # Add top product information
            top_product = insights['analysis_summary'].get('top_product', {})
            if top_product:
                response += f"### 🏆 Top Performing Product\n\n"
                response += f"- **Product**: {top_product.get('product_name', 'Unknown')}\n"
                response += f"- **Efficiency**: {top_product.get('efficiency', 0):.2f} mmol/g/h\n\n"
            
            # Add recommendations
            response += "## 💡 Recommendations\n\n"
            for recommendation in insights['recommendations']:
                response += f"{recommendation}\n\n"
            
            # Add visualization summary
            viz_summary = insights['visualization_summary']
            if viz_summary.get('total_files', 0) > 0:
                response += f"## 📊 Generated Visualizations\n\n"
                response += f"- **Total Files**: {viz_summary['total_files']}\n"
                response += f"- **Image Files**: {viz_summary['image_files']}\n"
                response += f"- **HTML Files**: {viz_summary['html_files']}\n\n"
                
                if viz_summary.get('file_list'):
                    response += "**Available Visualizations**:\n"
                    for file_info in viz_summary['file_list']:
                        response += f"- {file_info['name']} ({file_info['type']})\n"
                    response += "\n"
            
            # Add report summary
            report_summary = insights['report_summary']
            if report_summary.get('total_reports', 0) > 0:
                response += f"## 📋 Generated Reports\n\n"
                response += f"- **Total Reports**: {report_summary['total_reports']}\n"
                response += f"- **Report Types**: {', '.join(report_summary.get('report_types', []))}\n\n"
                
                if report_summary.get('report_list'):
                    response += "**Available Reports**:\n"
                    for report_info in report_summary['report_list']:
                        response += f"- {report_info['name']} ({report_info['type']})\n"
                    response += "\n"
            
            # Add next steps
            response += """
## 🚀 Next Steps

1. **Review the generated visualizations** to understand the analysis results
2. **Examine the detailed reports** for specific gene knockout recommendations
3. **Plan experimental validation** of the computational predictions
4. **Consider multi-gene knockout strategies** for enhanced effects
5. **Monitor strain performance** during implementation

## ⚠️ Important Notes

- All predictions are based on computational modeling and require experimental validation
- Gene knockout effects may vary under different growth conditions
- Consider regulatory and safety implications before implementation
- Monitor for unintended metabolic consequences

---
*Analysis performed using GeneDeletion Template System v1.0.0*
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error generating LLM response: {e}\n\nTraceback: {traceback.format_exc()}"
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """
        Get current analysis status
        
        Returns:
            Dict containing analysis status
        """
        return {
            'model_loaded': self.current_model is not None,
            'current_model': self.current_model,
            'results_available': bool(self.analysis_results),
            'analysis_completed': self.analysis_results.get('analysis_completed', False) if self.analysis_results else False
        }

# Global instance for easy access
gene_deletion_agent = GeneDeletionAnalysisAgent()

def analyze_gene_deletion_results(model_name: str, user_question: str = None) -> str:
    """
    Global function to analyze gene deletion results and provide LLM response
    
    Args:
        model_name (str): Name of the model to analyze
        user_question (str): Optional user question
        
    Returns:
        str: LLM response with analysis insights
    """
    try:
        # Load analysis results
        if not gene_deletion_agent.load_analysis_results(model_name):
            return f"❌ No analysis results found for model: {model_name}"
        
        # Generate LLM response
        return gene_deletion_agent.generate_llm_response(user_question)
        
    except Exception as e:
        return f"❌ Error analyzing gene deletion results: {e}\n\nTraceback: {traceback.format_exc()}"
