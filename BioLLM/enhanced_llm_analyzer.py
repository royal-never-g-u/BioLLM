#!/usr/bin/env python3
"""
Enhanced LLM Analyzer - Advanced analysis and interpretation of experiment results
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class EnhancedLLMAnalyzer:
    """
    Enhanced LLM analyzer for experiment results
    """
    
    def __init__(self):
        """Initialize the enhanced LLM analyzer"""
        pass
    
    def analyze_gene_deletion_results(self, experiment_result: Dict[str, Any]) -> str:
        """
        Generate comprehensive analysis for gene deletion results
        
        Args:
            experiment_result: Experiment results from execute_gene_deletion
            
        Returns:
            str: Comprehensive analysis report
        """
        if not experiment_result.get('success', False):
            return "❌ No valid results to analyze"
        
        analysis_results = experiment_result.get('results', {})
        if not analysis_results:
            return "⚠️ No analysis results found"
        
        # Generate comprehensive analysis
        report = self._generate_comprehensive_report(experiment_result, analysis_results)
        
        return report
    
    def _generate_comprehensive_report(self, experiment_result: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Generate comprehensive analysis report"""
        
        model_name = experiment_result.get('model_name', 'Unknown')
        timestamp = experiment_result.get('experiment_timestamp', 'Unknown')
        
        report = f"""
# 🔬 Gene Deletion Analysis Report

## 📋 Executive Summary

**Model**: {model_name}  
**Analysis Type**: Gene Knockout Analysis  
**Execution Time**: {timestamp}  
**Status**: ✅ Successfully Completed

---

## 🎯 Key Findings

{self._generate_key_findings(analysis_results)}

---

## 📊 Analysis Results

{self._generate_analysis_results(analysis_results)}

---

## 🧬 Gene Knockout Insights

{self._generate_knockout_insights(analysis_results)}

---

## 🧪 Product Optimization Analysis

{self._generate_product_analysis(analysis_results)}

---

## 🎯 Recommendations

{self._generate_recommendations(analysis_results)}

---

## 🔬 Biological Interpretation

{self._generate_biological_interpretation(analysis_results)}

---

## 📈 Next Steps

{self._generate_next_steps(analysis_results)}

---

*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def _generate_key_findings(self, analysis_results: Dict[str, Any]) -> str:
        """Generate key findings section"""
        findings = []
        
        summary = analysis_results.get('summary', {})
        
        # Extract key metrics
        if 'knockout_summary' in summary:
            knockout_summary = summary['knockout_summary']
            total_genes = knockout_summary.get('total_genes_analyzed', 0)
            effect_dist = knockout_summary.get('effect_distribution', {})
            
            findings.append(f"• **{total_genes} genes** were analyzed for knockout effects")
            findings.append("")
            
            if effect_dist:
                beneficial = effect_dist.get('beneficial', 0)
                neutral = effect_dist.get('neutral', 0)
                detrimental = effect_dist.get('detrimental', 0)
                
                findings.append(f"• **{beneficial} beneficial knockouts** identified")
                findings.append("")
                findings.append(f"• **{neutral} neutral knockouts** found")
                findings.append("")
                findings.append(f"• **{detrimental} detrimental knockouts** detected")
                findings.append("")
        
        if 'product_summary' in summary:
            product_summary = summary['product_summary']
            total_products = product_summary.get('total_products_analyzed', 0)
            successful_opt = product_summary.get('successful_optimizations', 0)
            
            findings.append(f"• **{total_products} products** were analyzed for optimization")
            findings.append("")
            findings.append(f"• **{successful_opt} successful optimizations** achieved")
            findings.append("")
        
        if not findings:
            findings.append("• Analysis completed successfully")
            findings.append("• Results are available for detailed review")
        
        return "\n".join(findings)
    
    def _generate_analysis_results(self, analysis_results: Dict[str, Any]) -> str:
        """Generate analysis results section"""
        results = []
        
        # Knockout analysis results
        if 'knockout_analysis' in analysis_results:
            knockout_data = analysis_results['knockout_analysis']
            if isinstance(knockout_data, pd.DataFrame) and not knockout_data.empty:
                beneficial_count = len(knockout_data[knockout_data.get('effect_category', '') == 'beneficial'])
                results.append(f"• **{beneficial_count} beneficial gene knockouts** identified")
                results.append("")
                
                if beneficial_count > 0:
                    top_improvement = knockout_data['production_improvement'].max()
                    results.append(f"• **Maximum production improvement**: {top_improvement:.2f}%")
                    results.append("")
        
        # Product optimization results
        if 'product_optimization' in analysis_results:
            product_data = analysis_results['product_optimization']
            if product_data and isinstance(product_data, dict):
                valid_products = {k: v for k, v in product_data.items() if v is not None}
                results.append(f"• **{len(valid_products)} products** successfully optimized")
                results.append("")
                
                if valid_products:
                    improvements = [v.get('improvement', 0) for v in valid_products.values()]
                    max_improvement = max(improvements) if improvements else 0
                    results.append(f"• **Maximum optimization improvement**: {max_improvement:.2f}%")
                    results.append("")
        
        if not results:
            results.append("• Analysis results are available in the detailed sections below")
        
        return "\n".join(results)
    
    def _generate_knockout_insights(self, analysis_results: Dict[str, Any]) -> str:
        """Generate gene knockout insights"""
        insights = []
        
        if 'knockout_analysis' in analysis_results:
            knockout_data = analysis_results['knockout_analysis']
            if isinstance(knockout_data, pd.DataFrame) and not knockout_data.empty:
                # Top beneficial knockouts
                beneficial_knockouts = knockout_data[
                    knockout_data.get('effect_category', '') == 'beneficial'
                ].head(5)
                
                if not beneficial_knockouts.empty:
                    insights.append("### 🏆 Top Beneficial Gene Knockouts")
                    insights.append("")
                    
                    for idx, row in beneficial_knockouts.iterrows():
                        gene_id = row.get('gene_id', 'Unknown')
                        improvement = row.get('production_improvement', 0)
                        growth_rate = row.get('growth_rate', 0)
                        
                        insights.append(f"**{gene_id}**: {improvement:.2f}% production improvement, {growth_rate:.4f} growth rate")
                    
                    insights.append("")
                
                # Effect distribution insights
                effect_dist = knockout_data.get('effect_category', '').value_counts()
                if not effect_dist.empty:
                    insights.append("### 📊 Knockout Effect Distribution")
                    insights.append("")
                    
                    for effect, count in effect_dist.items():
                        percentage = (count / len(knockout_data)) * 100
                        insights.append(f"• **{effect.title()}**: {count} genes ({percentage:.1f}%)")
                        insights.append("")
                    
                    insights.append("")
        
        if not insights:
            insights.append("• Gene knockout analysis completed")
            insights.append("")
            insights.append("• Detailed results available in the interactive dashboard")
            insights.append("")
        
        return "\n".join(insights)
    
    def _generate_product_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """Generate product optimization analysis"""
        analysis = []
        
        if 'product_optimization' in analysis_results:
            product_data = analysis_results['product_optimization']
            if product_data and isinstance(product_data, dict):
                valid_products = {k: v for k, v in product_data.items() if v is not None}
                
                if valid_products:
                    analysis.append("### 🧪 Product Optimization Results")
                    analysis.append("")
                    
                    # Top improvements
                    improvements = []
                    for product_name, data in valid_products.items():
                        improvement = data.get('improvement', 0)
                        improvements.append((product_name, improvement))
                    
                    improvements.sort(key=lambda x: x[1], reverse=True)
                    
                    analysis.append("#### 🏆 Top Product Improvements")
                    analysis.append("")
                    
                    for product_name, improvement in improvements[:5]:
                        analysis.append(f"• **{product_name}**: {improvement:.2f}% improvement")
                        analysis.append("")
                    
                    analysis.append("")
                    
                    # Overall statistics
                    avg_improvement = sum(imp for _, imp in improvements) / len(improvements)
                    max_improvement = max(imp for _, imp in improvements)
                    
                    analysis.append("#### 📈 Optimization Statistics")
                    analysis.append("")
                    analysis.append(f"• **Average improvement**: {avg_improvement:.2f}%")
                    analysis.append("")
                    analysis.append(f"• **Maximum improvement**: {max_improvement:.2f}%")
                    analysis.append("")
                    analysis.append(f"• **Products optimized**: {len(valid_products)}")
                    analysis.append("")
        
        if not analysis:
            analysis.append("• Product optimization analysis completed")
            analysis.append("")
            analysis.append("• Results available in the interactive dashboard")
            analysis.append("")
        
        return "\n".join(analysis)
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> str:
        """Generate recommendations based on results"""
        recommendations = []
        
        # Based on knockout analysis
        if 'knockout_analysis' in analysis_results:
            knockout_data = analysis_results['knockout_analysis']
            if isinstance(knockout_data, pd.DataFrame) and not knockout_data.empty:
                beneficial_count = len(knockout_data[knockout_data.get('effect_category', '') == 'beneficial'])
                
                if beneficial_count > 0:
                    recommendations.append("### 🎯 Gene Engineering Recommendations")
                    recommendations.append("")
                    recommendations.append("• **Prioritize beneficial gene knockouts** for experimental validation")
                    recommendations.append("")
                    recommendations.append("• **Focus on genes with highest production improvements**")
                    recommendations.append("")
                    recommendations.append("• **Consider growth rate trade-offs** when selecting targets")
                    recommendations.append("")
                    recommendations.append("• **Validate results with experimental data**")
                    recommendations.append("")
        
        # Based on product optimization
        if 'product_optimization' in analysis_results:
            product_data = analysis_results['product_optimization']
            if product_data and isinstance(product_data, dict):
                valid_products = {k: v for k, v in product_data.items() if v is not None}
                
                if valid_products:
                    recommendations.append("### 🧪 Production Optimization Recommendations")
                    recommendations.append("")
                    recommendations.append("• **Focus on products with highest improvement potential**")
                    recommendations.append("")
                    recommendations.append("• **Implement metabolic engineering strategies** for target products")
                    recommendations.append("")
                    recommendations.append("• **Monitor growth rates** during optimization")
                    recommendations.append("")
                    recommendations.append("• **Consider scale-up implications**")
                    recommendations.append("")
        
        # General recommendations
        recommendations.append("### 🔬 General Recommendations")
        recommendations.append("")
        recommendations.append("• **Perform experimental validation** of computational predictions")
        recommendations.append("")
        recommendations.append("• **Consider regulatory constraints** in gene engineering")
        recommendations.append("")
        recommendations.append("• **Monitor strain stability** after genetic modifications")
        recommendations.append("")
        recommendations.append("• **Optimize culture conditions** for maximum production")
        recommendations.append("")
        recommendations.append("• **Consider economic feasibility** of proposed modifications")
        
        return "\n".join(recommendations)
    
    def _generate_biological_interpretation(self, analysis_results: Dict[str, Any]) -> str:
        """Generate biological interpretation"""
        interpretation = []
        
        interpretation.append("### 🔬 Biological Insights")
        interpretation.append("")
        
        # Knockout interpretation
        if 'knockout_analysis' in analysis_results:
            knockout_data = analysis_results['knockout_analysis']
            if isinstance(knockout_data, pd.DataFrame) and not knockout_data.empty:
                beneficial_count = len(knockout_data[knockout_data.get('effect_category', '') == 'beneficial'])
                
                interpretation.append(f"• **{beneficial_count} beneficial knockouts** suggest potential for metabolic engineering")
                interpretation.append("")
                interpretation.append("• **Gene knockouts can redirect metabolic flux** toward desired products")
                interpretation.append("")
                interpretation.append("• **Growth rate changes** indicate metabolic network adaptations")
                interpretation.append("")
        
        # Product interpretation
        if 'product_optimization' in analysis_results:
            product_data = analysis_results['product_optimization']
            if product_data and isinstance(product_data, dict):
                valid_products = {k: v for k, v in product_data.items() if v is not None}
                
                if valid_products:
                    interpretation.append("• **Product optimization results** indicate metabolic network flexibility")
                    interpretation.append("")
                    interpretation.append("• **Production improvements** suggest underutilized metabolic pathways")
                    interpretation.append("")
                    interpretation.append("• **Metabolic engineering potential** is high for target products")
                    interpretation.append("")
        
        interpretation.append("### 🧬 Metabolic Network Implications")
        interpretation.append("")
        interpretation.append("• **Metabolic redundancy** allows for gene knockouts without lethal effects")
        interpretation.append("")
        interpretation.append("• **Flux redistribution** can enhance product formation")
        interpretation.append("")
        interpretation.append("• **Network robustness** enables multiple optimization strategies")
        interpretation.append("")
        interpretation.append("• **Evolutionary constraints** may limit some modifications")
        
        return "\n".join(interpretation)
    
    def _generate_next_steps(self, analysis_results: Dict[str, Any]) -> str:
        """Generate next steps recommendations"""
        steps = []
        
        steps.append("### 🚀 Recommended Next Steps")
        steps.append("")
        
        # Experimental validation
        steps.append("#### 1. Experimental Validation")
        steps.append("• **Design CRISPR experiments** for top beneficial gene knockouts")
        steps.append("")
        steps.append("• **Construct knockout strains** for validation")
        steps.append("")
        steps.append("• **Measure production rates** in engineered strains")
        steps.append("")
        steps.append("• **Compare computational vs experimental results**")
        steps.append("")
        
        # Further analysis
        steps.append("#### 2. Advanced Analysis")
        steps.append("• **Perform flux balance analysis** for detailed flux predictions")
        steps.append("")
        steps.append("• **Analyze metabolic pathway interactions**")
        steps.append("")
        steps.append("• **Investigate regulatory network effects**")
        steps.append("")
        steps.append("• **Consider multi-gene knockout strategies**")
        steps.append("")
        
        # Optimization
        steps.append("#### 3. Process Optimization")
        steps.append("• **Optimize culture conditions** for maximum production")
        steps.append("")
        steps.append("• **Scale up promising strains**")
        steps.append("")
        steps.append("• **Monitor strain stability** over time")
        steps.append("")
        steps.append("• **Evaluate economic feasibility**")
        steps.append("")
        
        # Documentation
        steps.append("#### 4. Documentation and Reporting")
        steps.append("• **Document all experimental procedures**")
        steps.append("")
        steps.append("• **Create detailed strain characterization reports**")
        steps.append("")
        steps.append("• **Prepare regulatory documentation** if needed")
        steps.append("")
        steps.append("• **Share results with research community**")
        
        return "\n".join(steps)

# Global instance
enhanced_llm_analyzer = EnhancedLLMAnalyzer()

def get_enhanced_llm_analyzer():
    """Get the global enhanced LLM analyzer instance"""
    return enhanced_llm_analyzer
