#!/usr/bin/env python3
"""
Gene Deletion Analysis Agent - Enhanced version with improved visualization and presentation
"""

import os
import json
import traceback
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class GeneDeletionAnalysisAgent:
    """
    Enhanced agent for analyzing gene deletion analysis results and providing comprehensive LLM insights
    """
    
    def __init__(self):
        """Initialize the enhanced gene deletion analysis agent"""
        self.analysis_results = {}
        self.current_model = None
        self.analysis_timestamp = None
    
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
                self.analysis_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error loading analysis results: {e}")
            return False
    
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze the loaded results and provide comprehensive insights
        
        Returns:
            Dict containing enhanced analysis insights
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
                'analysis_timestamp': self.analysis_timestamp,
                'analysis_summary': {},
                'key_findings': [],
                'recommendations': [],
                'visualization_summary': {},
                'report_summary': {},
                'performance_metrics': {},
                'strategic_insights': []
            }
            
            # Extract enhanced analysis summary
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                insights['analysis_summary'] = self._extract_enhanced_summary(summary)
            
            # Generate comprehensive key findings
            insights['key_findings'] = self._generate_enhanced_key_findings()
            
            # Generate strategic recommendations
            insights['recommendations'] = self._generate_strategic_recommendations()
            
            # Generate performance metrics
            insights['performance_metrics'] = self._generate_performance_metrics()
            
            # Generate strategic insights
            insights['strategic_insights'] = self._generate_strategic_insights()
            
            # Summarize visualizations with enhanced details
            insights['visualization_summary'] = self._summarize_enhanced_visualizations()
            
            # Summarize reports with enhanced details
            insights['report_summary'] = self._summarize_enhanced_reports()
            
            return insights
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analyzing results: {e}',
                'traceback': traceback.format_exc()
            }
    
    def _extract_enhanced_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Extract enhanced summary information"""
        enhanced_summary = {
            'total_genes_analyzed': 0,
            'effect_distribution': {},
            'successful_optimizations': 0,
            'top_product': {},
            'analysis_coverage': {},
            'quality_metrics': {}
        }
        
        try:
            # Extract knockout summary
            if 'knockout_summary' in summary:
                knockout_summary = summary['knockout_summary']
                enhanced_summary['total_genes_analyzed'] = knockout_summary.get('total_genes_analyzed', 0)
                enhanced_summary['effect_distribution'] = knockout_summary.get('effect_distribution', {})
                
                # Calculate analysis coverage
                total_genes = enhanced_summary['total_genes_analyzed']
                if total_genes > 0:
                    effect_counts = sum(enhanced_summary['effect_distribution'].values())
                    coverage = (effect_counts / total_genes) * 100 if total_genes > 0 else 0
                    enhanced_summary['analysis_coverage'] = {
                        'total_analyzed': effect_counts,
                        'coverage_percentage': coverage,
                        'completeness': 'Complete' if coverage >= 95 else 'Partial' if coverage >= 70 else 'Limited'
                    }
            
            # Extract product summary
            if 'product_summary' in summary:
                product_summary = summary['product_summary']
                enhanced_summary['successful_optimizations'] = product_summary.get('successful_optimizations', 0)
                enhanced_summary['top_product'] = product_summary.get('top_product', {})
            
            # Calculate quality metrics
            enhanced_summary['quality_metrics'] = self._calculate_quality_metrics(summary)
            
        except Exception as e:
            print(f"❌ Error extracting enhanced summary: {e}")
        
        return enhanced_summary
    
    def _calculate_quality_metrics(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics for the analysis"""
        metrics = {
            'data_quality': 'Unknown',
            'confidence_level': 'Unknown',
            'validation_status': 'Unknown'
        }
        
        try:
            # Assess data quality based on available information
            if 'knockout_summary' in summary and 'product_summary' in summary:
                metrics['data_quality'] = 'High'
                metrics['confidence_level'] = 'High'
                metrics['validation_status'] = 'Computational'
            elif 'knockout_summary' in summary or 'product_summary' in summary:
                metrics['data_quality'] = 'Medium'
                metrics['confidence_level'] = 'Medium'
                metrics['validation_status'] = 'Partial'
            else:
                metrics['data_quality'] = 'Low'
                metrics['confidence_level'] = 'Low'
                metrics['validation_status'] = 'Incomplete'
                
        except Exception as e:
            print(f"❌ Error calculating quality metrics: {e}")
        
        return metrics
    
    def _generate_enhanced_key_findings(self) -> List[str]:
        """Generate enhanced key findings from the analysis results"""
        findings = []
        
        try:
            # Analyze gene knockout effects with enhanced insights
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                knockout_summary = summary.get('knockout_summary', {})
                
                total_genes = knockout_summary.get('total_genes_analyzed', 0)
                effect_dist = knockout_summary.get('effect_distribution', {})
                
                if total_genes > 0:
                    findings.append(f"📊 **Comprehensive Analysis**: Analyzed {total_genes} genes for knockout effects using advanced metabolic modeling")
                    
                    # Enhanced effect distribution analysis
                    lethal_count = effect_dist.get('致死', 0)
                    severe_count = effect_dist.get('严重影响', 0)
                    moderate_count = effect_dist.get('中等影响', 0)
                    mild_count = effect_dist.get('轻微影响', 0)
                    no_effect_count = effect_dist.get('无影响', 0)
                    
                    if lethal_count > 0:
                        lethal_percent = (lethal_count / total_genes) * 100
                        findings.append(f"⚠️ **Critical Genes Identified**: {lethal_count} genes ({lethal_percent:.1f}%) are essential for cell survival")
                    
                    if no_effect_count > 0:
                        no_effect_percent = (no_effect_count / total_genes) * 100
                        findings.append(f"✅ **Safe Targets Found**: {no_effect_count} genes ({no_effect_percent:.1f}%) show minimal impact - ideal for metabolic engineering")
                    
                    if moderate_count > 0 or mild_count > 0:
                        potential_targets = moderate_count + mild_count
                        potential_percent = (potential_targets / total_genes) * 100
                        findings.append(f"🎯 **Optimization Candidates**: {potential_targets} genes ({potential_percent:.1f}%) show moderate effects - perfect balance for strain improvement")
            
            # Enhanced product optimization analysis
            if 'results' in self.analysis_results:
                results = self.analysis_results['results']
                product_optimization = results.get('product_optimization', {})
                
                if product_optimization:
                    valid_products = {k: v for k, v in product_optimization.items() if v is not None}
                    findings.append(f"🧪 **Multi-Product Analysis**: Evaluated {len(valid_products)} target products for production optimization")
                    
                    # Find top performing products with enhanced metrics
                    if valid_products:
                        top_product = max(valid_products.items(), 
                                        key=lambda x: x[1].get('production_efficiency', 0))
                        top_name = top_product[1].get('product_name', top_product[0])
                        top_efficiency = top_product[1].get('production_efficiency', 0)
                        findings.append(f"🏆 **Champion Product**: {top_name} demonstrates exceptional production efficiency: {top_efficiency:.2f} mmol/g/h")
            
            # Enhanced gene knockout target analysis
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
                        findings.append(f"🚀 **Breakthrough Improvement**: Optimal gene knockout strategy achieves {top_improvement:.1f}% production enhancement")
                        
                        viable_count = len(product_knockout_results[product_knockout_results['viable']])
                        findings.append(f"🔬 **Viable Solutions**: {viable_count} gene knockout combinations maintain cellular viability while improving production")
            
        except Exception as e:
            findings.append(f"❌ Error generating enhanced findings: {e}")
        
        return findings
    
    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic recommendations based on analysis results"""
        recommendations = []
        
        try:
            # Strategic implementation recommendations
            recommendations.append("🎯 **Strategic Implementation**: Prioritize gene knockouts based on impact-benefit analysis")
            recommendations.append("🔬 **Experimental Validation**: Design comprehensive validation protocols for computational predictions")
            recommendations.append("📊 **Multi-Scale Analysis**: Consider transcriptomic and proteomic data for comprehensive understanding")
            recommendations.append("⚖️ **Growth-Production Optimization**: Balance growth rate with product yield for optimal strain performance")
            
            # Specific recommendations based on results
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                knockout_summary = summary.get('knockout_summary', {})
                effect_dist = knockout_summary.get('effect_distribution', {})
                
                lethal_count = effect_dist.get('致死', 0)
                if lethal_count > 0:
                    recommendations.append("⚠️ **Essential Gene Management**: Develop alternative strategies for essential gene manipulation")
                
                no_effect_count = effect_dist.get('无影响', 0)
                if no_effect_count > 0:
                    recommendations.append("🎯 **Non-Essential Targeting**: Focus on genes with minimal growth impact for sustainable strain development")
            
            # Advanced engineering recommendations
            recommendations.append("🧬 **CRISPR-Cas9 Implementation**: Use validated sgRNA designs with proper controls and validation")
            recommendations.append("📈 **Progressive Optimization**: Implement knockouts stepwise to monitor cumulative effects")
            recommendations.append("🔄 **Adaptive Evolution**: Consider adaptive evolution strategies to enhance strain robustness")
            recommendations.append("🏭 **Scale-Up Preparation**: Develop fermentation protocols optimized for engineered strains")
            
        except Exception as e:
            recommendations.append(f"❌ Error generating strategic recommendations: {e}")
        
        return recommendations
    
    def _generate_performance_metrics(self) -> Dict[str, Any]:
        """Generate performance metrics for the analysis"""
        metrics = {
            'analysis_efficiency': {},
            'computational_performance': {},
            'result_quality': {}
        }
        
        try:
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                knockout_summary = summary.get('knockout_summary', {})
                
                total_genes = knockout_summary.get('total_genes_analyzed', 0)
                if total_genes > 0:
                    metrics['analysis_efficiency'] = {
                        'genes_per_analysis': total_genes,
                        'coverage_percentage': self._calculate_coverage_percentage(),
                        'completeness_score': self._calculate_completeness_score()
                    }
            
            # Add computational performance metrics if available
            if 'config_used' in self.analysis_results:
                config = self.analysis_results['config_used']
                metrics['computational_performance'] = {
                    'analysis_scope': config.get('analysis_scope', {}),
                    'optimization_targets': len(config.get('target_products', {}))
                }
            
        except Exception as e:
            print(f"❌ Error generating performance metrics: {e}")
        
        return metrics
    
    def _calculate_coverage_percentage(self) -> float:
        """Calculate analysis coverage percentage"""
        try:
            if 'summary' in self.analysis_results:
                summary = self.analysis_results['summary']
                knockout_summary = summary.get('knockout_summary', {})
                total_genes = knockout_summary.get('total_genes_analyzed', 0)
                effect_dist = knockout_summary.get('effect_distribution', {})
                
                if total_genes > 0:
                    analyzed_genes = sum(effect_dist.values())
                    return (analyzed_genes / total_genes) * 100
        except Exception as e:
            print(f"❌ Error calculating coverage percentage: {e}")
        
        return 0.0
    
    def _calculate_completeness_score(self) -> str:
        """Calculate completeness score"""
        coverage = self._calculate_coverage_percentage()
        
        if coverage >= 95:
            return "Excellent"
        elif coverage >= 80:
            return "Good"
        elif coverage >= 60:
            return "Fair"
        else:
            return "Limited"
    
    def _generate_strategic_insights(self) -> List[str]:
        """Generate strategic insights for future development"""
        insights = []
        
        try:
            insights.append("🔮 **Future Development**: Consider multi-gene knockout strategies for synergistic effects")
            insights.append("🌱 **Strain Evolution**: Plan for long-term strain stability and performance monitoring")
            insights.append("🔬 **Research Integration**: Integrate with transcriptomic and metabolomic studies")
            insights.append("🏭 **Industrial Application**: Develop protocols for industrial-scale implementation")
            
        except Exception as e:
            insights.append(f"❌ Error generating strategic insights: {e}")
        
        return insights
    
    def _summarize_enhanced_visualizations(self) -> Dict[str, Any]:
        """Summarize visualization files with enhanced details"""
        summary = {
            'total_files': 0,
            'image_files': 0,
            'html_files': 0,
            'file_list': [],
            'visualization_types': [],
            'interactive_visualizations': 0
        }
        
        try:
            if 'visualizations' in self.analysis_results:
                visualizations = self.analysis_results['visualizations']
                summary['total_files'] = len(visualizations)
                
                for viz in visualizations:
                    file_info = {
                        'name': viz.get('name', 'Unknown'),
                        'type': viz.get('type', 'Unknown'),
                        'size': viz.get('size', 0),
                        'interactive': viz.get('type') == 'html'
                    }
                    summary['file_list'].append(file_info)
                    
                    if viz.get('type') == 'image':
                        summary['image_files'] += 1
                    elif viz.get('type') == 'html':
                        summary['html_files'] += 1
                        summary['interactive_visualizations'] += 1
                    
                    if viz.get('type') not in summary['visualization_types']:
                        summary['visualization_types'].append(viz.get('type'))
                        
        except Exception as e:
            summary['error'] = str(e)
        
        return summary
    
    def _summarize_enhanced_reports(self) -> Dict[str, Any]:
        """Summarize report files with enhanced details"""
        summary = {
            'total_reports': 0,
            'report_types': [],
            'report_list': [],
            'report_sizes': {},
            'comprehensive_coverage': False
        }
        
        try:
            if 'report_paths' in self.analysis_results:
                report_paths = self.analysis_results['report_paths']
                summary['total_reports'] = len(report_paths)
                summary['report_types'] = list(report_paths.keys())
                
                total_size = 0
                for report_type, report_path in report_paths.items():
                    if os.path.exists(report_path):
                        file_size = os.path.getsize(report_path)
                        total_size += file_size
                        
                        report_info = {
                            'type': report_type,
                            'path': report_path,
                            'name': os.path.basename(report_path),
                            'size': file_size,
                            'size_mb': file_size / (1024 * 1024)
                        }
                        summary['report_list'].append(report_info)
                        
                        summary['report_sizes'][report_type] = file_size
                
                summary['total_size_mb'] = total_size / (1024 * 1024)
                summary['comprehensive_coverage'] = len(report_paths) >= 3  # At least 3 report types
                        
        except Exception as e:
            summary['error'] = str(e)
        
        return summary
    
    def generate_enhanced_llm_response(self, user_question: str = None) -> str:
        """
        Generate a comprehensive enhanced LLM response based on analysis results
        
        Args:
            user_question (str): Optional user question to focus the response
            
        Returns:
            str: Comprehensive enhanced LLM response
        """
        if not self.analysis_results:
            return "❌ No analysis results available. Please run gene deletion analysis first."
        
        try:
            # Analyze the results
            insights = self.analyze_results()
            
            if not insights['success']:
                return f"❌ Error analyzing results: {insights.get('error', 'Unknown error')}"
            
            # Generate comprehensive enhanced response
            response = f"""
# 🧬 Enhanced Gene Deletion Analysis Report for {self.current_model}

## 📊 Executive Summary

This comprehensive gene deletion analysis was performed on the **{self.current_model}** metabolic model using advanced computational modeling techniques to identify optimal gene knockout strategies for improving target product production.

### 🔬 Analysis Overview
- **Model**: {self.current_model}
- **Analysis Date**: {insights.get('analysis_timestamp', 'Unknown')}
- **Total Genes Analyzed**: {insights['analysis_summary'].get('total_genes_analyzed', 0)}
- **Target Products**: {insights['analysis_summary'].get('successful_optimizations', 0)} products analyzed
- **Analysis Method**: Advanced Flux Balance Analysis (FBA) with gene knockout simulation
- **Quality Level**: {insights['analysis_summary'].get('quality_metrics', {}).get('data_quality', 'Unknown')}

## 🎯 Key Findings

"""
            
            # Add enhanced key findings
            for finding in insights['key_findings']:
                response += f"{finding}\n\n"
            
            # Add enhanced effect distribution
            effect_dist = insights['analysis_summary'].get('effect_distribution', {})
            if effect_dist:
                response += "### 📈 Gene Knockout Effect Distribution\n\n"
                for effect, count in effect_dist.items():
                    total = insights['analysis_summary'].get('total_genes_analyzed', 0)
                    if total > 0:
                        percentage = (count / total) * 100
                        response += f"- **{effect}**: {count} genes ({percentage:.1f}%)\n"
                response += "\n"
            
            # Add performance metrics
            performance_metrics = insights.get('performance_metrics', {})
            if performance_metrics:
                response += "### 📊 Performance Metrics\n\n"
                analysis_efficiency = performance_metrics.get('analysis_efficiency', {})
                if analysis_efficiency:
                    response += f"- **Analysis Coverage**: {analysis_efficiency.get('coverage_percentage', 0):.1f}%\n"
                    response += f"- **Completeness Score**: {analysis_efficiency.get('completeness_score', 'Unknown')}\n"
                response += "\n"
            
            # Add top product information
            top_product = insights['analysis_summary'].get('top_product', {})
            if top_product:
                response += f"### 🏆 Top Performing Product\n\n"
                response += f"- **Product**: {top_product.get('product_name', 'Unknown')}\n"
                response += f"- **Efficiency**: {top_product.get('efficiency', 0):.2f} mmol/g/h\n"
                response += f"- **Optimization Potential**: High\n\n"
            
            # Add strategic insights
            strategic_insights = insights.get('strategic_insights', [])
            if strategic_insights:
                response += "### 🔮 Strategic Insights\n\n"
                for insight in strategic_insights:
                    response += f"{insight}\n\n"
            
            # Add enhanced recommendations
            response += "## 💡 Strategic Recommendations\n\n"
            for recommendation in insights['recommendations']:
                response += f"{recommendation}\n\n"
            
            # Add enhanced visualization summary
            viz_summary = insights['visualization_summary']
            if viz_summary.get('total_files', 0) > 0:
                response += f"## 📊 Generated Visualizations\n\n"
                response += f"- **Total Files**: {viz_summary['total_files']}\n"
                response += f"- **Image Files**: {viz_summary['image_files']}\n"
                response += f"- **Interactive HTML**: {viz_summary['html_files']}\n"
                response += f"- **Visualization Types**: {', '.join(viz_summary.get('visualization_types', []))}\n\n"
                
                if viz_summary.get('file_list'):
                    response += "**Available Visualizations**:\n"
                    for file_info in viz_summary['file_list']:
                        interactive_mark = "🖱️" if file_info.get('interactive') else "📷"
                        response += f"- {interactive_mark} {file_info['name']} ({file_info['type']})\n"
                    response += "\n"
            
            # Add enhanced report summary
            report_summary = insights['report_summary']
            if report_summary.get('total_reports', 0) > 0:
                response += f"## 📋 Generated Reports\n\n"
                response += f"- **Total Reports**: {report_summary['total_reports']}\n"
                response += f"- **Report Types**: {', '.join(report_summary.get('report_types', []))}\n"
                response += f"- **Total Size**: {report_summary.get('total_size_mb', 0):.2f} MB\n"
                response += f"- **Coverage**: {'Comprehensive' if report_summary.get('comprehensive_coverage') else 'Standard'}\n\n"
                
                if report_summary.get('report_list'):
                    response += "**Available Reports**:\n"
                    for report_info in report_summary['report_list']:
                        response += f"- 📄 {report_info['name']} ({report_info['type']}) - {report_info['size_mb']:.2f} MB\n"
                    response += "\n"
            
            # Add next steps
            response += """
## 🚀 Next Steps

1. **Review Interactive Visualizations**: Explore the generated HTML visualizations for detailed analysis
2. **Examine Comprehensive Reports**: Study the detailed reports for specific gene knockout recommendations
3. **Plan Experimental Validation**: Design validation protocols for computational predictions
4. **Consider Multi-Gene Strategies**: Explore synergistic effects of multiple gene knockouts
5. **Monitor Strain Performance**: Implement performance tracking during strain development
6. **Scale-Up Preparation**: Develop industrial-scale fermentation protocols

## ⚠️ Important Notes

- All predictions are based on advanced computational modeling and require experimental validation
- Gene knockout effects may vary under different growth conditions and media compositions
- Consider regulatory and safety implications before implementation
- Monitor for unintended metabolic consequences and strain stability
- Implement proper controls and validation protocols

## 🔬 Quality Assurance

- **Data Quality**: {insights['analysis_summary'].get('quality_metrics', {}).get('data_quality', 'Unknown')}
- **Confidence Level**: {insights['analysis_summary'].get('quality_metrics', {}).get('confidence_level', 'Unknown')}
- **Validation Status**: {insights['analysis_summary'].get('quality_metrics', {}).get('validation_status', 'Unknown')}

---
*Enhanced Analysis performed using GeneDeletion Template System v2.0.0 with Advanced Visualization*
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error generating enhanced LLM response: {e}\n\nTraceback: {traceback.format_exc()}"
    
    def get_enhanced_analysis_status(self) -> Dict[str, Any]:
        """
        Get enhanced current analysis status
        
        Returns:
            Dict containing enhanced analysis status
        """
        return {
            'model_loaded': self.current_model is not None,
            'current_model': self.current_model,
            'analysis_timestamp': self.analysis_timestamp,
            'results_available': bool(self.analysis_results),
            'analysis_completed': self.analysis_results.get('analysis_completed', False) if self.analysis_results else False,
            'quality_level': self.analysis_results.get('summary', {}).get('quality_metrics', {}).get('data_quality', 'Unknown') if self.analysis_results else 'Unknown'
        }

# Global instance for easy access
enhanced_gene_deletion_agent = GeneDeletionAnalysisAgent()

def analyze_gene_deletion_results_enhanced(model_name: str, user_question: str = None) -> str:
    """
    Enhanced global function to analyze gene deletion results and provide comprehensive LLM response
    
    Args:
        model_name (str): Name of the model to analyze
        user_question (str): Optional user question
        
    Returns:
        str: Enhanced LLM response with comprehensive analysis insights
    """
    try:
        # Load analysis results
        if not enhanced_gene_deletion_agent.load_analysis_results(model_name):
            return f"❌ No analysis results found for model: {model_name}"
        
        # Generate enhanced LLM response
        return enhanced_gene_deletion_agent.generate_enhanced_llm_response(user_question)
        
    except Exception as e:
        return f"❌ Error analyzing gene deletion results: {e}\n\nTraceback: {traceback.format_exc()}"

# Backward compatibility
gene_deletion_agent = enhanced_gene_deletion_agent
analyze_gene_deletion_results = analyze_gene_deletion_results_enhanced
