#!/usr/bin/env python3
"""
Enhanced Result Visualizer - Advanced visualization and presentation for experiment results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from typing import Dict, Any, List, Optional
import numpy as np
import datetime

class EnhancedResultVisualizer:
    """
    Enhanced result visualizer with advanced visualization and presentation capabilities
    """
    
    def __init__(self):
        """Initialize the enhanced result visualizer"""
        self.setup_plotly_config()
        self.setup_streamlit_config()
    
    def setup_plotly_config(self):
        """Setup enhanced Plotly configuration"""
        import plotly.io as pio
        pio.templates.default = "plotly_white"
        
        # Configure for better display
        pio.renderers.default = "browser"
    
    def setup_streamlit_config(self):
        """Setup Streamlit configuration for better display"""
        st.set_page_config(
            page_title="BioLLM Enhanced Analysis",
            page_icon="🧬",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def visualize_gene_deletion_results_enhanced(self, experiment_result: Dict[str, Any]) -> None:
        """
        Enhanced visualization of gene deletion analysis results
        
        Args:
            experiment_result: Experiment results from execute_gene_deletion
        """
        if not experiment_result.get('success', False):
            st.error("❌ No valid results to visualize")
            return
        
        # Display enhanced header
        self._display_enhanced_header(experiment_result)
        
        # Get analysis results
        analysis_results = experiment_result.get('results', {})
        if not analysis_results:
            st.warning("⚠️ No analysis results found")
            return
        
        # Create tabs for better organization
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Executive Summary", 
            "🔬 Detailed Analysis", 
            "📈 Visualizations", 
            "📋 Reports", 
            "🎯 Recommendations"
        ])
        
        with tab1:
            self._display_executive_summary(experiment_result, analysis_results)
        
        with tab2:
            self._display_enhanced_detailed_results(analysis_results)
        
        with tab3:
            self._display_enhanced_visualizations(experiment_result)
        
        with tab4:
            self._display_enhanced_reports(experiment_result)
        
        with tab5:
            self._display_strategic_recommendations(analysis_results)
    
    def _display_enhanced_header(self, experiment_result: Dict[str, Any]) -> None:
        """Display enhanced header with comprehensive information"""
        st.markdown("""
        # 🧬 Enhanced Gene Deletion Analysis Results
        
        ---
        """)
        
        # Create a comprehensive info panel
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Model", 
                experiment_result.get('model_name', 'Unknown'),
                help="Metabolic model analyzed"
            )
        
        with col2:
            st.metric(
                "Analysis Status", 
                "✅ Completed" if experiment_result.get('success') else "❌ Failed",
                help="Analysis completion status"
            )
        
        with col3:
            timestamp = experiment_result.get('experiment_timestamp', 'Unknown')
            st.metric(
                "Execution Time", 
                timestamp,
                help="When the analysis was performed"
            )
        
        with col4:
            # Calculate analysis duration if available
            duration = "N/A"
            if 'analysis_duration' in experiment_result:
                duration = f"{experiment_result['analysis_duration']:.1f}s"
            st.metric(
                "Duration", 
                duration,
                help="Analysis execution time"
            )
        
        st.markdown("---")
    
    def _display_executive_summary(self, experiment_result: Dict[str, Any], analysis_results: Dict[str, Any]) -> None:
        """Display comprehensive executive summary"""
        st.markdown("## 📊 Executive Summary")
        
        # Get summary data
        summary = analysis_results.get('summary', {})
        if not summary:
            st.info("No summary information available")
            return
        
        # Key metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'knockout_summary' in summary:
                total_genes = summary['knockout_summary'].get('total_genes_analyzed', 0)
                st.metric(
                    "Genes Analyzed", 
                    f"{total_genes:,}",
                    help="Total number of genes analyzed for knockout effects"
                )
        
        with col2:
            if 'product_summary' in summary:
                successful_optimizations = summary['product_summary'].get('successful_optimizations', 0)
                st.metric(
                    "Products Optimized", 
                    successful_optimizations,
                    help="Number of products successfully optimized"
                )
        
        with col3:
            if 'knockout_summary' in summary:
                effect_dist = summary['knockout_summary'].get('effect_distribution', {})
                lethal_count = effect_dist.get('致死', 0)
                st.metric(
                    "Lethal Genes", 
                    lethal_count,
                    delta=f"{(lethal_count/sum(effect_dist.values())*100):.1f}%" if sum(effect_dist.values()) > 0 else "0%",
                    delta_color="inverse",
                    help="Number of genes that are lethal when knocked out"
                )
        
        with col4:
            if 'knockout_summary' in summary:
                effect_dist = summary['knockout_summary'].get('effect_distribution', {})
                no_effect_count = effect_dist.get('无影响', 0)
                st.metric(
                    "Safe Targets", 
                    no_effect_count,
                    delta=f"{(no_effect_count/sum(effect_dist.values())*100):.1f}%" if sum(effect_dist.values()) > 0 else "0%",
                    delta_color="normal",
                    help="Number of genes with minimal impact - ideal for engineering"
                )
        
        # Effect distribution visualization
        if 'knockout_summary' in summary:
            effect_dist = summary['knockout_summary'].get('effect_distribution', {})
            if effect_dist:
                st.markdown("### 📈 Gene Knockout Effect Distribution")
                
                # Create enhanced pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=list(effect_dist.keys()),
                    values=list(effect_dist.values()),
                    hole=0.4,
                    marker_colors=['#FF6B6B', '#FFE66D', '#4ECDC4', '#45B7D1', '#96CEB4'],
                    textinfo='label+percent+value',
                    textfont_size=12
                )])
                
                fig.update_layout(
                    title="Distribution of Gene Knockout Effects",
                    showlegend=True,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"executive_summary_effect_distribution_pie_{id(fig)}")
        
        # Top product information
        if 'product_summary' in summary:
            top_product = summary['product_summary'].get('top_product', {})
            if top_product:
                st.markdown("### 🏆 Top Performing Product")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Product Name",
                        top_product.get('product_name', 'Unknown')
                    )
                
                with col2:
                    st.metric(
                        "Production Efficiency",
                        f"{top_product.get('efficiency', 0):.2f} mmol/g/h"
                    )
                
                with col3:
                    st.metric(
                        "Optimization Status",
                        "✅ Optimized"
                    )
    
    def _display_enhanced_detailed_results(self, analysis_results: Dict[str, Any]) -> None:
        """Display enhanced detailed analysis results"""
        st.markdown("## 🔬 Detailed Analysis Results")
        
        # Get detailed results
        results = analysis_results.get('results', {})
        if not results:
            st.info("📊 Analysis completed successfully. Processing detailed results...")
            
            # Provide default detailed analysis content
            st.markdown("### 📋 Analysis Components")
            st.markdown("""
            The Constraint-Based Analysis includes the following components:
            
            **1. Basic Model Information**
            - Model structure and composition
            - Reaction and metabolite counts
            - Gene-reaction associations
            
            **2. Flux Balance Analysis (FBA)**
            - Optimal growth rate calculation
            - Flux distribution analysis
            - Objective function optimization
            
            **3. Growth Analysis**
            - Aerobic vs anaerobic growth comparison
            - Carbon source utilization patterns
            - Environmental condition responses
            
            **4. Essentiality Analysis**
            - Essential reaction identification
            - Network robustness assessment
            - Metabolic flexibility evaluation
            
            **5. Environmental Analysis**
            - pH sensitivity analysis
            - Temperature effects on growth
            - Stress response assessment
            """)
            
            # Show available data structure
            st.markdown("### 🔍 Available Data Structure")
            if analysis_results:
                st.json(analysis_results)
            
            return
        
        # Display basic model information
        if 'basic_info' in results:
            basic_info = results['basic_info']
            st.markdown("### 📊 Model Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Model Name**: {basic_info.get('name', 'Unknown')}")
                st.markdown(f"**Reactions**: {basic_info.get('reactions_count', 0):,}")
                st.markdown(f"**Metabolites**: {basic_info.get('metabolites_count', 0):,}")
                st.markdown(f"**Genes**: {basic_info.get('genes_count', 0):,}")
            
            with col2:
                st.markdown(f"**Compartments**: {basic_info.get('compartments_count', 'N/A')}")
                st.markdown(f"**Exchange Reactions**: {basic_info.get('exchange_reactions_count', 'N/A')}")
                st.markdown(f"**Transport Reactions**: {basic_info.get('transport_reactions_count', 'N/A')}")
                st.markdown(f"**Objective Function**: {basic_info.get('objective_function', 'N/A')}")
        else:
            st.markdown("### 📊 Model Information")
            st.info("Model information not available in results")
        
        # Display FBA analysis
        if 'fba_analysis' in results:
            fba_analysis = results['fba_analysis']
            st.markdown("### ⚖️ Flux Balance Analysis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if fba_analysis.get('objective_value') is not None:
                    st.metric(
                        "Growth Rate",
                        f"{fba_analysis.get('objective_value', 0):.6f} h⁻¹"
                    )
                else:
                    st.metric("Growth Rate", "N/A")
            
            with col2:
                st.metric(
                    "Status",
                    fba_analysis.get('status', 'Unknown')
                )
            
            with col3:
                if 'fluxes' in fba_analysis and fba_analysis['fluxes']:
                    fluxes = fba_analysis['fluxes']
                    non_zero_fluxes = sum(1 for flux in fluxes.values() if abs(flux) > 1e-6)
                    st.metric(
                        "Non-zero Fluxes",
                        f"{non_zero_fluxes:,}"
                    )
                else:
                    st.metric("Non-zero Fluxes", "N/A")
            
            # Show flux distribution if available
            if 'fluxes' in fba_analysis and fba_analysis['fluxes']:
                st.markdown("#### 📈 Top Flux Reactions")
                fluxes = fba_analysis['fluxes']
                flux_data = []
                for reaction, flux in fluxes.items():
                    if abs(flux) > 1e-6:  # Only show significant fluxes
                        flux_data.append({
                            'Reaction': reaction,
                            'Flux': flux
                        })
                
                if flux_data:
                    # Sort by absolute flux value
                    flux_data.sort(key=lambda x: abs(x['Flux']), reverse=True)
                    df_flux = pd.DataFrame(flux_data[:20])  # Show top 20
                    
                    st.dataframe(
                        df_flux,
                        column_config={
                            "Flux": st.column_config.NumberColumn(
                                "Flux (mmol/gDW/h)",
                                format="%.6f"
                            )
                        },
                        hide_index=True
                    )
        else:
            st.markdown("### ⚖️ Flux Balance Analysis")
            st.info("FBA analysis results not available")
        
        # Display growth analysis
        if 'growth_analysis' in results:
            growth_analysis = results['growth_analysis']
            st.markdown("### 🌱 Growth Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if growth_analysis.get('aerobic_growth') is not None:
                    aerobic_growth = growth_analysis.get('aerobic_growth', 0)
                    st.metric(
                        "Aerobic Growth",
                        f"{aerobic_growth:.6f} h⁻¹"
                    )
                else:
                    st.metric("Aerobic Growth", "N/A")
            
            with col2:
                if growth_analysis.get('anaerobic_growth') is not None:
                    anaerobic_growth = growth_analysis.get('anaerobic_growth', 0)
                    st.metric(
                        "Anaerobic Growth",
                        f"{anaerobic_growth:.6f} h⁻¹"
                    )
                else:
                    st.metric("Anaerobic Growth", "N/A")
            
            with col3:
                if (growth_analysis.get('aerobic_growth') is not None and 
                    growth_analysis.get('anaerobic_growth') is not None):
                    aerobic = growth_analysis.get('aerobic_growth', 0)
                    anaerobic = growth_analysis.get('anaerobic_growth', 0)
                    if aerobic > 0:
                        growth_reduction = ((aerobic - anaerobic) / aerobic) * 100
                        st.metric(
                            "Growth Reduction",
                            f"{growth_reduction:.1f}%"
                        )
                    else:
                        st.metric("Growth Reduction", "N/A")
                else:
                    st.metric("Growth Reduction", "N/A")
            
            # Carbon source analysis
            if 'carbon_source_growth' in growth_analysis:
                carbon_growth = growth_analysis['carbon_source_growth']
                if isinstance(carbon_growth, dict) and carbon_growth:
                    st.markdown("#### 📊 Carbon Source Growth Rates")
                    
                    carbon_data = []
                    for source, rate in carbon_growth.items():
                        carbon_data.append({
                            'Carbon Source': source,
                            'Growth Rate (h⁻¹)': rate
                        })
                    
                    if carbon_data:
                        df_carbon = pd.DataFrame(carbon_data)
                        df_carbon = df_carbon.sort_values('Growth Rate (h⁻¹)', ascending=False)
                        
                        st.dataframe(
                            df_carbon,
                            column_config={
                                "Growth Rate (h⁻¹)": st.column_config.NumberColumn(
                                    "Growth Rate (h⁻¹)",
                                    format="%.6f"
                                )
                            },
                            hide_index=True
                        )
                        
                        # Create visualization
                        fig = px.bar(
                            df_carbon,
                            x='Carbon Source',
                            y='Growth Rate (h⁻¹)',
                            title="Growth Rates on Different Carbon Sources",
                            color='Growth Rate (h⁻¹)',
                            color_continuous_scale='viridis'
                        )
                        
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 🌱 Growth Analysis")
            st.info("Growth analysis results not available")
        
        # Display environmental analysis
        if 'environmental_analysis' in results:
            environmental_analysis = results['environmental_analysis']
            st.markdown("### 🌡️ Environmental Analysis")
            
            # pH analysis
            if 'ph_analysis' in environmental_analysis:
                ph_analysis = environmental_analysis['ph_analysis']
                if isinstance(ph_analysis, dict) and ph_analysis:
                    st.markdown("#### 📊 pH Effects on Growth")
                    
                    ph_data = []
                    for condition, data in ph_analysis.items():
                        if isinstance(data, dict):
                            ph_data.append({
                                'pH Condition': condition,
                                'Growth Rate (h⁻¹)': data.get('growth_rate', 0)
                            })
                    
                    if ph_data:
                        df_ph = pd.DataFrame(ph_data)
                        
                        st.dataframe(
                            df_ph,
                            column_config={
                                "Growth Rate (h⁻¹)": st.column_config.NumberColumn(
                                    "Growth Rate (h⁻¹)",
                                    format="%.6f"
                                )
                            },
                            hide_index=True
                        )
                        
                        # Create visualization
                        fig = px.line(
                            df_ph,
                            x='pH Condition',
                            y='Growth Rate (h⁻¹)',
                            title="Growth Rate vs pH Conditions",
                            markers=True
                        )
                        
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("pH analysis data not available in expected format")
            else:
                st.info("pH analysis not performed")
            
            # Temperature analysis
            if 'temperature_analysis' in environmental_analysis:
                temp_analysis = environmental_analysis['temperature_analysis']
                if isinstance(temp_analysis, dict) and temp_analysis:
                    st.markdown("#### 🌡️ Temperature Effects on Growth")
                    
                    temp_data = []
                    for condition, data in temp_analysis.items():
                        if isinstance(data, dict):
                            temp_data.append({
                                'Temperature Condition': condition,
                                'Growth Rate (h⁻¹)': data.get('growth_rate', 0)
                            })
                    
                    if temp_data:
                        df_temp = pd.DataFrame(temp_data)
                        
                        st.dataframe(
                            df_temp,
                            column_config={
                                "Growth Rate (h⁻¹)": st.column_config.NumberColumn(
                                    "Growth Rate (h⁻¹)",
                                    format="%.6f"
                                )
                            },
                            hide_index=True
                        )
                        
                        # Create visualization
                        fig = px.bar(
                            df_temp,
                            x='Temperature Condition',
                            y='Growth Rate (h⁻¹)',
                            title="Growth Rate vs Temperature Conditions",
                            color='Growth Rate (h⁻¹)',
                            color_continuous_scale='plasma'
                        )
                        
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Temperature analysis data not available in expected format")
            else:
                st.info("Temperature analysis not performed")
        else:
            st.markdown("### 🌡️ Environmental Analysis")
            st.info("Environmental analysis results not available")
        
        # Display essentiality analysis
        if 'essentiality_analysis' in results:
            essentiality_analysis = results['essentiality_analysis']
            st.markdown("### 🔬 Essentiality Analysis")
            
            if 'essential_reactions' in essentiality_analysis and essentiality_analysis['essential_reactions']:
                essential_reactions = essentiality_analysis['essential_reactions']
                total_tested = essentiality_analysis.get('total_tested', len(essential_reactions))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Essential Reactions", len(essential_reactions))
                with col2:
                    st.metric("Total Tested", total_tested)
                
                # Show essential reactions
                st.markdown("#### 🎯 Essential Reactions")
                if len(essential_reactions) <= 20:
                    for i, reaction in enumerate(essential_reactions, 1):
                        st.markdown(f"{i}. **{reaction}**")
                else:
                    st.markdown(f"**First 20 essential reactions:**")
                    for i, reaction in enumerate(essential_reactions[:20], 1):
                        st.markdown(f"{i}. **{reaction}**")
                    st.markdown(f"... and {len(essential_reactions) - 20} more")
            else:
                st.info("Essential reactions data not available")
        else:
            st.markdown("### 🔬 Essentiality Analysis")
            st.info("Essentiality analysis results not available")
        
        # Show raw results if available
        if results:
            with st.expander("🔍 Raw Analysis Results"):
                st.json(results)
    
    def _display_enhanced_visualizations(self, experiment_result: Dict[str, Any]) -> None:
        """Display enhanced visualizations"""
        st.markdown("## 📈 Generated Visualizations")
        
        # First try to get visualizations from experiment_result
        visualizations = experiment_result.get('visualizations', [])
        
        # If no visualizations in experiment_result, scan the analysis_results directory
        if not visualizations:
            model_name = experiment_result.get('model_name', '')
            if model_name:
                visualizations = self._scan_analysis_visualizations(model_name)
        
        if not visualizations:
            st.info("No visualizations available")
            return
        
        # Group visualizations by type
        image_files = [v for v in visualizations if v.get('type') == 'image']
        html_files = [v for v in visualizations if v.get('type') == 'html']
        
        # Display interactive HTML visualizations
        if html_files:
            st.markdown("### 🖱️ Interactive Visualizations")
            
            for viz in html_files:
                with st.expander(f"📊 {viz.get('name', 'Unknown')}", expanded=True):
                    try:
                        # Read and display HTML content
                        if os.path.exists(viz.get('path', '')):
                            with open(viz.get('path', ''), 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            st.components.v1.html(html_content, height=600)
                        else:
                            st.warning(f"File not found: {viz.get('path', '')}")
                    except Exception as e:
                        st.error(f"Error displaying visualization: {e}")
        
        # Display static image visualizations
        if image_files:
            st.markdown("### 📷 Static Visualizations")
            
            for viz in image_files:
                with st.expander(f"📷 {viz.get('name', 'Unknown')}", expanded=True):
                    try:
                        if os.path.exists(viz.get('path', '')):
                            st.image(viz.get('path', ''), use_container_width=True)
                        else:
                            st.warning(f"File not found: {viz.get('path', '')}")
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
        
        # Visualization summary
        st.markdown("### 📊 Visualization Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", len(visualizations))
        
        with col2:
            st.metric("Interactive", len(html_files))
        
        with col3:
            st.metric("Static Images", len(image_files))
    
    def _display_enhanced_reports(self, experiment_result: Dict[str, Any]) -> None:
        """Display enhanced report information"""
        st.markdown("## 📋 Generated Reports")
        
        # Get report information from analysis results
        analysis_results = experiment_result.get('results', {})
        report_paths = analysis_results.get('report_paths', {})
        
        if not report_paths:
            st.info("No reports available")
            return
        
        # Display report summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Reports", len(report_paths))
        
        with col2:
            total_size = sum(os.path.getsize(path) for path in report_paths.values() if os.path.exists(path))
            st.metric("Total Size", f"{total_size / (1024*1024):.2f} MB")
        
        with col3:
            available_reports = sum(1 for path in report_paths.values() if os.path.exists(path))
            st.metric("Available", available_reports)
        
        # Display individual reports
        st.markdown("### 📄 Available Reports")
        
        for report_type, report_path in report_paths.items():
            with st.expander(f"📄 {report_type.replace('_', ' ').title()}", expanded=True):
                if os.path.exists(report_path):
                    # Get file info
                    file_size = os.path.getsize(report_path)
                    file_size_mb = file_size / (1024 * 1024)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("File Size", f"{file_size_mb:.2f} MB")
                    
                    with col2:
                        st.metric("Status", "✅ Available")
                    
                    with col3:
                        # Add download button
                        with open(report_path, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        st.download_button(
                            label="📥 Download Report",
                            data=report_content,
                            file_name=os.path.basename(report_path),
                            mime="text/plain",
                            key=f"download_report_{os.path.basename(report_path)}_{id(report_content)}"
                        )
                    
                    # Display report preview
                    if report_path.endswith('.txt') or report_path.endswith('.md'):
                        with open(report_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Show first 500 characters as preview
                        preview = content[:500] + "..." if len(content) > 500 else content
                        st.text_area("Report Preview", preview, height=200, disabled=True, key=f"report_preview_{os.path.basename(report_path)}_{id(content)}")
                else:
                    st.warning(f"Report file not found: {report_path}")
    
    def _display_strategic_recommendations(self, analysis_results: Dict[str, Any]) -> None:
        """Display strategic recommendations"""
        st.markdown("## 🎯 Strategic Recommendations")
        
        # Generate recommendations based on analysis results
        recommendations = self._generate_recommendations_from_results(analysis_results)
        
        # Display recommendations in organized sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔬 Experimental Recommendations")
            exp_recs = [r for r in recommendations if "experimental" in r.lower() or "validation" in r.lower()]
            for rec in exp_recs:
                st.markdown(f"- {rec}")
        
        with col2:
            st.markdown("### 🧬 Engineering Recommendations")
            eng_recs = [r for r in recommendations if "engineering" in r.lower() or "crispr" in r.lower()]
            for rec in eng_recs:
                st.markdown(f"- {rec}")
        
        st.markdown("### 📊 Analysis Recommendations")
        analysis_recs = [r for r in recommendations if "analysis" in r.lower() or "monitoring" in r.lower()]
        for rec in analysis_recs:
            st.markdown(f"- {rec}")
        
        st.markdown("### 🚀 Implementation Recommendations")
        impl_recs = [r for r in recommendations if "implementation" in r.lower() or "scale" in r.lower()]
        for rec in impl_recs:
            st.markdown(f"- {rec}")
    
    def _generate_recommendations_from_results(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Base recommendations
        recommendations.extend([
            "🔬 **Experimental Validation**: Design comprehensive validation protocols for computational predictions",
            "📊 **Multi-Scale Analysis**: Consider transcriptomic and proteomic data for comprehensive understanding",
            "⚖️ **Growth-Production Optimization**: Balance growth rate with product yield for optimal strain performance",
            "🧬 **CRISPR-Cas9 Implementation**: Use validated sgRNA designs with proper controls and validation",
            "📈 **Progressive Optimization**: Implement knockouts stepwise to monitor cumulative effects",
            "🔄 **Adaptive Evolution**: Consider adaptive evolution strategies to enhance strain robustness",
            "🏭 **Scale-Up Preparation**: Develop fermentation protocols optimized for engineered strains",
            "🔮 **Future Development**: Consider multi-gene knockout strategies for synergistic effects",
            "🌱 **Strain Evolution**: Plan for long-term strain stability and performance monitoring",
            "🔬 **Research Integration**: Integrate with transcriptomic and metabolomic studies"
        ])
        
        # Specific recommendations based on results
        if 'summary' in analysis_results:
            summary = analysis_results['summary']
            knockout_summary = summary.get('knockout_summary', {})
            effect_dist = knockout_summary.get('effect_distribution', {})
            
            lethal_count = effect_dist.get('致死', 0)
            if lethal_count > 0:
                recommendations.append("⚠️ **Essential Gene Management**: Develop alternative strategies for essential gene manipulation")
            
            no_effect_count = effect_dist.get('无影响', 0)
            if no_effect_count > 0:
                recommendations.append("🎯 **Non-Essential Targeting**: Focus on genes with minimal growth impact for sustainable strain development")
        
        return recommendations
    
    def create_interactive_dashboard(self, experiment_result: Dict[str, Any]) -> None:
        """
        Create an interactive dashboard for the results (backward compatibility)
        
        Args:
            experiment_result: Experiment results from execute_gene_deletion
        """
        # Use the enhanced visualization method for backward compatibility
        self.visualize_gene_deletion_results_enhanced(experiment_result)
    
    def visualize_gene_deletion_results(self, experiment_result: Dict[str, Any]) -> None:
        """
        Visualize gene deletion analysis results (backward compatibility)
        
        Args:
            experiment_result: Experiment results from execute_gene_deletion
        """
        # Use the enhanced visualization method for backward compatibility
        self.visualize_gene_deletion_results_enhanced(experiment_result)

    def visualize_constraint_based_analysis_results(self, experiment_result: Dict[str, Any]) -> None:
        """
        Visualize Constraint-Based Analysis results
        
        Args:
            experiment_result: Experiment results from execute_constraint_based_analysis
        """
        if not experiment_result.get('success', False):
            st.error("❌ No valid results to visualize")
            return
        
        # Display enhanced header
        self._display_constraint_based_enhanced_header(experiment_result)
        
        # Get analysis results
        analysis_results = experiment_result.get('results', {})
        if not analysis_results:
            st.warning("⚠️ No analysis results found")
            return
        
        # Check data availability for each section
        has_visualizations = self._has_constraint_based_visualizations_data(experiment_result)
        has_generated_reports = self._has_constraint_based_generated_reports_data(experiment_result)
        has_strategic_recommendations = self._has_constraint_based_strategic_recommendations_data(analysis_results)
        
        # Create dynamic tabs based on available data
        tabs = []
        tab_functions = []
        
        if has_visualizations:
            tabs.append("📈 Generated Visualizations")
            tab_functions.append(lambda: self._display_constraint_based_visualizations(experiment_result))
        
        if has_generated_reports:
            tabs.append("📋 Generated Reports")
            tab_functions.append(lambda: self._display_constraint_based_generated_reports(experiment_result))
        
        if has_strategic_recommendations:
            tabs.append("🎯 Strategic Recommendations")
            tab_functions.append(lambda: self._display_constraint_based_strategic_recommendations(analysis_results))
        
        # If no data available, show a message
        if not tabs:
            st.info("📊 Analysis completed successfully, but no detailed results are available for display.")
            return
        
        # Create tabs for better organization
        if len(tabs) == 1:
            # If only one tab, display content directly without tabs
            tab_functions[0]()
        else:
            # Create tabs and display content
            tab_objects = st.tabs(tabs)
            for i, tab in enumerate(tab_objects):
                with tab:
                    tab_functions[i]()
    
    def _has_constraint_based_visualizations_data(self, experiment_result: Dict[str, Any]) -> bool:
        """Check if visualization data is available for Constraint-Based Analysis"""
        # Check for visualizations in experiment_result
        visualizations = experiment_result.get('visualizations', [])
        if visualizations:
            return True
        
        # Check for model name to scan directories
        model_name = experiment_result.get('model_name', '')
        if model_name:
            scanned_visualizations = self._scan_analysis_visualizations(model_name)
            if scanned_visualizations:
                return True
        
        return False
    
    def _has_constraint_based_generated_reports_data(self, experiment_result: Dict[str, Any]) -> bool:
        """Check if generated reports data is available for Constraint-Based Analysis"""
        # Check for report files in experiment_result
        results = experiment_result.get('results', {})
        if results:
            data_files = results.get('data_files', {})
            if data_files:
                # Check for report files
                report_files = [f for f in data_files.keys() if 'report' in f.lower() or f.endswith('.txt')]
                if report_files:
                    return True
        
        # Check for model name to scan for report files
        model_name = experiment_result.get('model_name', '')
        if model_name:
            # Check for report files in analysis_results directory
            analysis_dir = os.path.join(os.path.dirname(__file__), 'analysis_results', model_name)
            if os.path.exists(analysis_dir):
                report_files = [f for f in os.listdir(analysis_dir) if f.endswith(('.txt', '.md', '.html'))]
                if report_files:
                    return True
        
        return False
    
    def _has_constraint_based_strategic_recommendations_data(self, analysis_results: Dict[str, Any]) -> bool:
        """Check if strategic recommendations data is available for Constraint-Based Analysis"""
        results = analysis_results.get('results', {})
        if not results:
            return False
        
        detailed_results = results.get('results', {})
        data_files = results.get('data_files', {})
        
        # Check for recommendations in detailed results
        if detailed_results:
            if 'recommendations' in detailed_results:
                return True
            
            # Check for analysis results that could generate recommendations
            if any(key in detailed_results for key in ['growth_analysis', 'environmental_analysis', 'nutrient_analysis']):
                return True
        
        # Check data files
        if data_files:
            if 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
                analysis_data = data_files['analysis_results.json']
                if 'recommendations' in analysis_data:
                    return True
                
                # Check for analysis results
                if any(key in analysis_data for key in ['growth_analysis', 'environmental_analysis', 'nutrient_analysis']):
                    return True
        
        return False

    def _display_constraint_based_enhanced_header(self, experiment_result: Dict[str, Any]) -> None:
        """Display enhanced header with comprehensive information"""
        st.markdown("""
        # 🔬 Enhanced Constraint-Based Analysis Results
        
        ---
        """)
        
        # Create a comprehensive info panel
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Model", 
                experiment_result.get('model_name', 'Unknown'),
                help="Metabolic model analyzed"
            )
        
        with col2:
            st.metric(
                "Analysis Status", 
                "✅ Completed" if experiment_result.get('success') else "❌ Failed",
                help="Analysis completion status"
            )
        
        with col3:
            timestamp = experiment_result.get('experiment_timestamp', 'Unknown')
            st.metric(
                "Execution Time", 
                timestamp,
                help="When the analysis was performed"
            )
        
        with col4:
            # Calculate analysis duration if available
            duration = "N/A"
            if 'analysis_duration' in experiment_result:
                duration = f"{experiment_result['analysis_duration']:.1f}s"
            st.metric(
                "Duration", 
                duration,
                help="Analysis execution time"
            )
        
        st.markdown("---")
    
    def _display_constraint_based_executive_summary(self, experiment_result: Dict[str, Any], analysis_results: Dict[str, Any]) -> None:
        """Display comprehensive executive summary for Constraint-Based Analysis"""
        st.markdown("## 📊 Executive Summary")
        
        # Get summary data
        summary = analysis_results.get('summary', {})
        results = analysis_results.get('results', {})
        
        if not summary and not results:
            st.info("No summary information available")
            return
        
        # Extract model information from results
        model_info = results.get('basic_info', {})
        fba_results = results.get('fba_analysis', {})
        growth_results = results.get('growth_analysis', {})
        essentiality_results = results.get('essentiality_analysis', {})
        
        # Key metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            reactions_count = model_info.get('reactions_count', 0)
            st.metric(
                "Reactions", 
                f"{reactions_count:,}",
                help="Total number of reactions in model"
            )
        
        with col2:
            metabolites_count = model_info.get('metabolites_count', 0)
            st.metric(
                "Metabolites", 
                f"{metabolites_count:,}",
                help="Total number of metabolites in model"
            )
        
        with col3:
            genes_count = model_info.get('genes_count', 0)
            st.metric(
                "Genes", 
                f"{genes_count:,}",
                help="Total number of genes in model"
            )
        
        with col4:
            if fba_results:
                growth_rate = fba_results.get('objective_value', 0)
                st.metric(
                    "Optimal Growth Rate", 
                    f"{growth_rate:.4f} h⁻¹",
                    help="Maximum predicted growth rate"
                )
        
        # Analysis overview
        st.markdown("### 🔬 Analysis Overview")
        
        # Create overview metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if growth_results:
                aerobic_growth = growth_results.get('aerobic_growth', 0)
                st.metric(
                    "Aerobic Growth",
                    f"{aerobic_growth:.4f} h⁻¹",
                    help="Growth rate under aerobic conditions"
                )
        
        with col2:
            if growth_results:
                anaerobic_growth = growth_results.get('anaerobic_growth', 0)
                st.metric(
                    "Anaerobic Growth",
                    f"{anaerobic_growth:.4f} h⁻¹",
                    help="Growth rate under anaerobic conditions"
                )
        
        with col3:
            if essentiality_results:
                essential_count = len(essentiality_results.get('essential_reactions', []))
                total_tested = essentiality_results.get('total_tested', 0)
                st.metric(
                    "Essential Reactions",
                    f"{essential_count}/{total_tested}",
                    help="Number of essential reactions found"
                )
        
        # Key findings summary
        st.markdown("### 🎯 Key Findings")
        
        findings = []
        
        if model_info:
            findings.append(f"**Model**: {model_info.get('name', 'Unknown')} with {reactions_count:,} reactions and {metabolites_count:,} metabolites")
        
        if fba_results:
            growth_rate = fba_results.get('objective_value', 0)
            status = fba_results.get('status', 'Unknown')
            findings.append(f"**Optimal Growth**: {growth_rate:.4f} h⁻¹ (Status: {status})")
        
        if growth_results:
            aerobic = growth_results.get('aerobic_growth', 0)
            anaerobic = growth_results.get('anaerobic_growth', 0)
            reduction = growth_results.get('growth_reduction_anaerobic', 0)
            findings.append(f"**Oxygen Dependency**: Aerobic {aerobic:.4f} h⁻¹, Anaerobic {anaerobic:.4f} h⁻¹ ({reduction:.1f}% reduction)")
        
        if essentiality_results:
            essential_count = len(essentiality_results.get('essential_reactions', []))
            findings.append(f"**Network Robustness**: {essential_count} essential reactions identified out of {total_tested} tested")
        
        for finding in findings:
            st.markdown(f"• {finding}")
        
        # Model description
        if model_info:
            st.markdown("### 📋 Model Description")
            st.markdown(f"**Model Name**: {model_info.get('name', 'Unknown')}")
            st.markdown(f"**Compartments**: {model_info.get('compartments_count', 0)}")
            st.markdown(f"**Exchange Reactions**: {model_info.get('exchange_reactions_count', 0)}")
            st.markdown(f"**Transport Reactions**: {model_info.get('transport_reactions_count', 0)}")
    
    def _display_constraint_based_detailed_analysis_results(self, analysis_results: Dict[str, Any]) -> None:
        """Display detailed Constraint-Based Analysis results"""
        st.markdown("## 🔬 Detailed Analysis Results")
        
        # Get detailed results
        results = analysis_results.get('results', {})
        if not results:
            st.info("📊 Analysis completed successfully. Processing detailed results...")
            
            # Provide default detailed analysis content
            st.markdown("### 📋 Analysis Components")
            st.markdown("""
            The Constraint-Based Analysis includes the following components:
            
            **1. Basic Model Information**
            - Model structure and composition
            - Reaction and metabolite counts
            - Gene-reaction associations
            
            **2. Flux Balance Analysis (FBA)**
            - Optimal growth rate calculation
            - Flux distribution analysis
            - Objective function optimization
            
            **3. Growth Analysis**
            - Aerobic vs anaerobic growth comparison
            - Carbon source utilization patterns
            - Environmental condition responses
            
            **4. Essentiality Analysis**
            - Essential reaction identification
            - Network robustness assessment
            - Metabolic flexibility evaluation
            
            **5. Environmental Analysis**
            - pH sensitivity analysis
            - Temperature effects on growth
            - Stress response assessment
            """)
            
            # Show available data structure
            st.markdown("### 🔍 Available Data Structure")
            if analysis_results:
                st.json(analysis_results)
            
            return
        
        # Display basic model information
        if 'basic_info' in results:
            basic_info = results['basic_info']
            st.markdown("### 📊 Model Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Model Name**: {basic_info.get('name', 'Unknown')}")
                st.markdown(f"**Reactions**: {basic_info.get('reactions_count', 0):,}")
                st.markdown(f"**Metabolites**: {basic_info.get('metabolites_count', 0):,}")
                st.markdown(f"**Genes**: {basic_info.get('genes_count', 0):,}")
            
            with col2:
                st.markdown(f"**Compartments**: {basic_info.get('compartments_count', 'N/A')}")
                st.markdown(f"**Exchange Reactions**: {basic_info.get('exchange_reactions_count', 'N/A')}")
                st.markdown(f"**Transport Reactions**: {basic_info.get('transport_reactions_count', 'N/A')}")
                st.markdown(f"**Objective Function**: {basic_info.get('objective_function', 'N/A')}")
        else:
            st.markdown("### 📊 Model Information")
            st.info("Model information not available in results")
        
        # Display FBA analysis
        if 'fba_analysis' in results:
            fba_analysis = results['fba_analysis']
            st.markdown("### ⚖️ Flux Balance Analysis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if fba_analysis.get('objective_value') is not None:
                    st.metric(
                        "Growth Rate",
                        f"{fba_analysis.get('objective_value', 0):.6f} h⁻¹"
                    )
                else:
                    st.metric("Growth Rate", "N/A")
            
            with col2:
                st.metric(
                    "Status",
                    fba_analysis.get('status', 'Unknown')
                )
            
            with col3:
                if 'fluxes' in fba_analysis and fba_analysis['fluxes']:
                    fluxes = fba_analysis['fluxes']
                    non_zero_fluxes = sum(1 for flux in fluxes.values() if abs(flux) > 1e-6)
                    st.metric(
                        "Non-zero Fluxes",
                        f"{non_zero_fluxes:,}"
                    )
                else:
                    st.metric("Non-zero Fluxes", "N/A")
            
            # Show flux distribution if available
            if 'fluxes' in fba_analysis and fba_analysis['fluxes']:
                st.markdown("#### 📈 Top Flux Reactions")
                fluxes = fba_analysis['fluxes']
                flux_data = []
                for reaction, flux in fluxes.items():
                    if abs(flux) > 1e-6:  # Only show significant fluxes
                        flux_data.append({
                            'Reaction': reaction,
                            'Flux': flux
                        })
                
                if flux_data:
                    # Sort by absolute flux value
                    flux_data.sort(key=lambda x: abs(x['Flux']), reverse=True)
                    df_flux = pd.DataFrame(flux_data[:20])  # Show top 20
                    
                    st.dataframe(
                        df_flux,
                        column_config={
                            "Flux": st.column_config.NumberColumn(
                                "Flux (mmol/gDW/h)",
                                format="%.6f"
                            )
                        },
                        hide_index=True
                    )
        else:
            st.markdown("### ⚖️ Flux Balance Analysis")
            st.info("FBA analysis results not available")
        
        # Display growth analysis
        if 'growth_analysis' in results:
            growth_analysis = results['growth_analysis']
            st.markdown("### 🌱 Growth Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if growth_analysis.get('aerobic_growth') is not None:
                    aerobic_growth = growth_analysis.get('aerobic_growth', 0)
                    st.metric(
                        "Aerobic Growth",
                        f"{aerobic_growth:.6f} h⁻¹"
                    )
                else:
                    st.metric("Aerobic Growth", "N/A")
            
            with col2:
                if growth_analysis.get('anaerobic_growth') is not None:
                    anaerobic_growth = growth_analysis.get('anaerobic_growth', 0)
                    st.metric(
                        "Anaerobic Growth",
                        f"{anaerobic_growth:.6f} h⁻¹"
                    )
                else:
                    st.metric("Anaerobic Growth", "N/A")
            
            with col3:
                if (growth_analysis.get('aerobic_growth') is not None and 
                    growth_analysis.get('anaerobic_growth') is not None):
                    aerobic = growth_analysis.get('aerobic_growth', 0)
                    anaerobic = growth_analysis.get('anaerobic_growth', 0)
                    if aerobic > 0:
                        growth_reduction = ((aerobic - anaerobic) / aerobic) * 100
                        st.metric(
                            "Growth Reduction",
                            f"{growth_reduction:.1f}%"
                        )
                    else:
                        st.metric("Growth Reduction", "N/A")
                else:
                    st.metric("Growth Reduction", "N/A")
            
            # Carbon source analysis
            if 'carbon_source_growth' in growth_analysis:
                carbon_growth = growth_analysis['carbon_source_growth']
                if isinstance(carbon_growth, dict) and carbon_growth:
                    st.markdown("#### 📊 Carbon Source Growth Rates")
                    
                    carbon_data = []
                    for source, rate in carbon_growth.items():
                        carbon_data.append({
                            'Carbon Source': source,
                            'Growth Rate (h⁻¹)': rate
                        })
                    
                    if carbon_data:
                        df_carbon = pd.DataFrame(carbon_data)
                        df_carbon = df_carbon.sort_values('Growth Rate (h⁻¹)', ascending=False)
                        
                        st.dataframe(
                            df_carbon,
                            column_config={
                                "Growth Rate (h⁻¹)": st.column_config.NumberColumn(
                                    "Growth Rate (h⁻¹)",
                                    format="%.6f"
                                )
                            },
                            hide_index=True
                        )
                        
                        # Create visualization
                        fig = px.bar(
                            df_carbon,
                            x='Carbon Source',
                            y='Growth Rate (h⁻¹)',
                            title="Growth Rates on Different Carbon Sources",
                            color='Growth Rate (h⁻¹)',
                            color_continuous_scale='viridis'
                        )
                        
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 🌱 Growth Analysis")
            st.info("Growth analysis results not available")
        
        # Display environmental analysis
        if 'environmental_analysis' in results:
            environmental_analysis = results['environmental_analysis']
            st.markdown("### 🌡️ Environmental Analysis")
            
            # pH analysis
            if 'ph_analysis' in environmental_analysis:
                ph_analysis = environmental_analysis['ph_analysis']
                if isinstance(ph_analysis, dict) and ph_analysis:
                    st.markdown("#### 📊 pH Effects on Growth")
                    
                    ph_data = []
                    for condition, data in ph_analysis.items():
                        if isinstance(data, dict):
                            ph_data.append({
                                'pH Condition': condition,
                                'Growth Rate (h⁻¹)': data.get('growth_rate', 0)
                            })
                    
                    if ph_data:
                        df_ph = pd.DataFrame(ph_data)
                        
                        st.dataframe(
                            df_ph,
                            column_config={
                                "Growth Rate (h⁻¹)": st.column_config.NumberColumn(
                                    "Growth Rate (h⁻¹)",
                                    format="%.6f"
                                )
                            },
                            hide_index=True
                        )
                        
                        # Create visualization
                        fig = px.line(
                            df_ph,
                            x='pH Condition',
                            y='Growth Rate (h⁻¹)',
                            title="Growth Rate vs pH Conditions",
                            markers=True
                        )
                        
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("pH analysis data not available in expected format")
            else:
                st.info("pH analysis not performed")
            
            # Temperature analysis
            if 'temperature_analysis' in environmental_analysis:
                temp_analysis = environmental_analysis['temperature_analysis']
                if isinstance(temp_analysis, dict) and temp_analysis:
                    st.markdown("#### 🌡️ Temperature Effects on Growth")
                    
                    temp_data = []
                    for condition, data in temp_analysis.items():
                        if isinstance(data, dict):
                            temp_data.append({
                                'Temperature Condition': condition,
                                'Growth Rate (h⁻¹)': data.get('growth_rate', 0)
                            })
                    
                    if temp_data:
                        df_temp = pd.DataFrame(temp_data)
                        
                        st.dataframe(
                            df_temp,
                            column_config={
                                "Growth Rate (h⁻¹)": st.column_config.NumberColumn(
                                    "Growth Rate (h⁻¹)",
                                    format="%.6f"
                                )
                            },
                            hide_index=True
                        )
                        
                        # Create visualization
                        fig = px.bar(
                            df_temp,
                            x='Temperature Condition',
                            y='Growth Rate (h⁻¹)',
                            title="Growth Rate vs Temperature Conditions",
                            color='Growth Rate (h⁻¹)',
                            color_continuous_scale='plasma'
                        )
                        
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Temperature analysis data not available in expected format")
            else:
                st.info("Temperature analysis not performed")
        else:
            st.markdown("### 🌡️ Environmental Analysis")
            st.info("Environmental analysis results not available")
        
        # Display essentiality analysis
        if 'essentiality_analysis' in results:
            essentiality_analysis = results['essentiality_analysis']
            st.markdown("### 🔬 Essentiality Analysis")
            
            if 'essential_reactions' in essentiality_analysis and essentiality_analysis['essential_reactions']:
                essential_reactions = essentiality_analysis['essential_reactions']
                total_tested = essentiality_analysis.get('total_tested', len(essential_reactions))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Essential Reactions", len(essential_reactions))
                with col2:
                    st.metric("Total Tested", total_tested)
                
                # Show essential reactions
                st.markdown("#### 🎯 Essential Reactions")
                if len(essential_reactions) <= 20:
                    for i, reaction in enumerate(essential_reactions, 1):
                        st.markdown(f"{i}. **{reaction}**")
                else:
                    st.markdown(f"**First 20 essential reactions:**")
                    for i, reaction in enumerate(essential_reactions[:20], 1):
                        st.markdown(f"{i}. **{reaction}**")
                    st.markdown(f"... and {len(essential_reactions) - 20} more")
            else:
                st.info("Essential reactions data not available")
        else:
            st.markdown("### 🔬 Essentiality Analysis")
            st.info("Essentiality analysis results not available")
        
        # Show raw results if available
        if results:
            with st.expander("🔍 Raw Analysis Results"):
                st.json(results)
    
    def _display_constraint_based_generated_reports(self, experiment_result: Dict[str, Any]) -> None:
        """Display generated reports for Constraint-Based Analysis"""
        st.markdown("## 📋 Generated Reports")
        
        # Get report information from analysis results
        analysis_results = experiment_result.get('results', {})
        results = analysis_results.get('results', {})
        
        # Check for generated files
        output_directory = analysis_results.get('output_directory', '')
        files_generated = results.get('files_generated', [])
        
        if not files_generated and not output_directory:
            st.info("No reports available")
            return
        
        # Display report summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", len(files_generated))
        
        with col2:
            if output_directory and os.path.exists(output_directory):
                total_size = sum(os.path.getsize(os.path.join(output_directory, f)) 
                               for f in os.listdir(output_directory) 
                               if os.path.isfile(os.path.join(output_directory, f)))
                st.metric("Total Size", f"{total_size / (1024*1024):.2f} MB")
            else:
                st.metric("Total Size", "N/A")
        
        with col3:
            if output_directory and os.path.exists(output_directory):
                available_files = len([f for f in os.listdir(output_directory) 
                                     if os.path.isfile(os.path.join(output_directory, f))])
                st.metric("Available", available_files)
            else:
                st.metric("Available", 0)
        
        # Display individual files
        st.markdown("### 📄 Generated Files")
        
        if output_directory and os.path.exists(output_directory):
            for file in os.listdir(output_directory):
                file_path = os.path.join(output_directory, file)
                if os.path.isfile(file_path):
                    with st.expander(f"📄 {file}", expanded=False):
                        # Get file info
                        file_size = os.path.getsize(file_path)
                        file_size_mb = file_size / (1024 * 1024)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("File Size", f"{file_size_mb:.2f} MB")
                        
                        with col2:
                            st.metric("File Type", os.path.splitext(file)[1].upper())
                        
                        with col3:
                            st.metric("Status", "✅ Available")
                        
                        # Display file content if it's a text file
                        if file.endswith('.txt') or file.endswith('.md'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    file_content = f.read()
                                st.text_area("File Content", file_content, height=300)
                            except Exception as e:
                                st.error(f"Error reading file: {e}")
                        elif file.endswith('.json'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    json_content = json.load(f)
                                st.json(json_content)
                            except Exception as e:
                                st.error(f"Error reading JSON file: {e}")
                        elif file.endswith('.html'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                st.components.v1.html(html_content, height=600)
                            except Exception as e:
                                st.error(f"Error reading HTML file: {e}")
                        elif file.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                            st.image(file_path, caption=file)
        
        # Display data files from results
        data_files = results.get('data_files', {})
        if data_files:
            st.markdown("### 📊 Analysis Data Files")
            
            for file_name, data in data_files.items():
                with st.expander(f"📊 {file_name}", expanded=False):
                    if isinstance(data, dict):
                        st.json(data)
                    elif isinstance(data, str):
                        st.text_area("File Content", data, height=200)
                    else:
                        st.write(data)
        
        # Display LLM-generated report if available
        if 'report' in experiment_result:
            st.markdown("### 🤖 AI-Generated Report")
            with st.expander("📋 Comprehensive Analysis Report", expanded=True):
                st.markdown(experiment_result['report'])
    
    def _display_constraint_based_strategic_recommendations(self, analysis_results: Dict[str, Any]) -> None:
        """Display strategic recommendations for Constraint-Based Analysis"""
        st.markdown("## 🎯 Strategic Recommendations")
        
        # Get analysis data
        results = analysis_results.get('results', {})
        summary = analysis_results.get('summary', {})
        
        # Generate recommendations based on analysis results
        recommendations = []
        
        # Based on growth analysis
        if 'growth_analysis' in results:
            growth_analysis = results['growth_analysis']
            
            if 'carbon_source_growth' in growth_analysis:
                carbon_growth = growth_analysis['carbon_source_growth']
                if isinstance(carbon_growth, dict) and carbon_growth:
                    # Find best carbon source
                    best_source = max(carbon_growth.items(), key=lambda x: x[1])
                    recommendations.append(f"• **Optimal carbon source**: {best_source[0]} with growth rate {best_source[1]:.6f} h⁻¹")
                    recommendations.append("• **Carbon source optimization** - Use results for media design")
        
        # Based on environmental analysis
        if 'environmental_analysis' in results:
            environmental_analysis = results['environmental_analysis']
            
            if 'ph_analysis' in environmental_analysis:
                recommendations.append("• **pH optimization analyzed** - Use results for culture condition optimization")
            
            if 'temperature_analysis' in environmental_analysis:
                recommendations.append("• **Temperature effects analyzed** - Consider temperature control strategies")
        
        # Based on nutrient analysis
        if 'nutrient_analysis' in results:
            nutrient_analysis = results['nutrient_analysis']
            
            if 'essential_nutrients' in nutrient_analysis:
                essential_count = len(nutrient_analysis['essential_nutrients'])
                recommendations.append(f"• **{essential_count} essential nutrients identified** - Ensure adequate supply")
                recommendations.append("• **Nutrient supplementation** - Consider adding identified essential nutrients")
        
        # General constraint-based analysis recommendations
        recommendations.extend([
            "• **Validate predictions** with experimental growth measurements",
            "• **Optimize culture conditions** based on environmental analysis results",
            "• **Design media formulations** using carbon source and nutrient analysis",
            "• **Monitor environmental parameters** during cultivation",
            "• **Scale up with consideration** of identified constraints"
        ])
        
        # Display recommendations
        for recommendation in recommendations:
            st.markdown(recommendation)
        
        # Add next steps
        st.markdown("### 🚀 Next Steps")
        st.markdown("""
        1. **Media Optimization**: Design optimal growth media based on carbon source analysis
        2. **Environmental Control**: Implement pH and temperature control based on analysis results
        3. **Nutrient Supplementation**: Add essential nutrients identified in the analysis
        4. **Experimental Validation**: Test predicted optimal conditions in laboratory
        5. **Process Development**: Apply insights to industrial-scale fermentation processes
        """)

    def visualize_fba_results(self, experiment_result: Dict[str, Any]) -> None:
        """
        Visualize FBA analysis results
        
        Args:
            experiment_result: Experiment results from execute_fba
        """
        if not experiment_result.get('success', False):
            st.error("❌ No valid results to visualize")
            return
        
        # Display enhanced header
        self._display_fba_enhanced_header(experiment_result)
        
        # Get analysis results
        analysis_results = experiment_result.get('results', {})
        if not analysis_results:
            st.warning("⚠️ No analysis results found")
            return
        
        # Check data availability for each section
        has_executive_summary = self._has_fba_executive_summary_data(experiment_result, analysis_results)
        has_detailed_analysis = self._has_fba_detailed_analysis_data(analysis_results)
        has_visualizations = self._has_fba_visualizations_data(experiment_result)
        has_generated_reports = self._has_fba_generated_reports_data(experiment_result)
        has_strategic_recommendations = self._has_fba_strategic_recommendations_data(analysis_results)
        
        # Create dynamic tabs based on available data
        tabs = []
        tab_functions = []
        
        if has_executive_summary:
            tabs.append("📊 Executive Summary")
            tab_functions.append(lambda: self._display_fba_executive_summary(experiment_result, analysis_results))
        
        if has_detailed_analysis:
            tabs.append("🔬 Detailed Analysis Results")
            tab_functions.append(lambda: self._display_fba_detailed_analysis_results(analysis_results))
        
        if has_visualizations:
            tabs.append("📈 Generated Visualizations")
            tab_functions.append(lambda: self._display_fba_visualizations(experiment_result))
        
        if has_generated_reports:
            tabs.append("📋 Generated Reports")
            tab_functions.append(lambda: self._display_fba_generated_reports(experiment_result))
        
        if has_strategic_recommendations:
            tabs.append("🎯 Strategic Recommendations")
            tab_functions.append(lambda: self._display_fba_strategic_recommendations(analysis_results))
        
        # If no data available, show a message
        if not tabs:
            st.info("📊 Analysis completed successfully, but no detailed results are available for display.")
            return
        
        # Create tabs for better organization
        if len(tabs) == 1:
            # If only one tab, display content directly without tabs
            tab_functions[0]()
        else:
            # Create tabs and display content
            tab_objects = st.tabs(tabs)
            for i, tab in enumerate(tab_objects):
                with tab:
                    tab_functions[i]()
    
    def _has_fba_executive_summary_data(self, experiment_result: Dict[str, Any], analysis_results: Dict[str, Any]) -> bool:
        """Check if executive summary data is available"""
        summary = analysis_results.get('summary', {})
        results = analysis_results.get('results', {})
        
        # Extract data from results
        detailed_results = results.get('results', {}) if results else {}
        data_files = results.get('data_files', {}) if results else {}
        
        # Try to get model info from different sources
        model_info = None
        if 'model_info' in detailed_results:
            model_info = detailed_results['model_info']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            model_info = data_files['analysis_results.json'].get('model_info', {})
        
        # Try to get FBA results from different sources
        fba_results = None
        if 'fba_analysis' in detailed_results:
            fba_results = detailed_results['fba_analysis']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            fba_results = data_files['analysis_results.json'].get('fba_analysis', {})
        
        # Check if we have valid metrics (same logic as in _display_fba_executive_summary)
        valid_metrics_count = 0
        
        # Check Growth Rate
        if fba_results and fba_results.get('objective_value') is not None:
            valid_metrics_count += 1
        
        # Check Solution Status
        if fba_results and fba_results.get('status'):
            valid_metrics_count += 1
        
        # Check Reactions Count
        if model_info and model_info.get('reactions_count') is not None:
            valid_metrics_count += 1
        
        # Check Metabolites Count
        if model_info and model_info.get('metabolites_count') is not None:
            valid_metrics_count += 1
        
        # Check Genes Count
        if model_info and model_info.get('genes_count') is not None:
            valid_metrics_count += 1
        
        # Check Non-zero Fluxes
        if fba_results and fba_results.get('flux_distribution'):
            valid_metrics_count += 1
        
        # Check Model ID
        if model_info and model_info.get('model_id'):
            valid_metrics_count += 1
        
        # Only return True if we have at least one valid metric
        return valid_metrics_count > 0
    
    def _has_fba_detailed_analysis_data(self, analysis_results: Dict[str, Any]) -> bool:
        """Check if detailed analysis data is available"""
        results = analysis_results.get('results', {})
        if not results:
            return False
        
        detailed_results = results.get('results', {})
        data_files = results.get('data_files', {})
        
        # Check for detailed analysis components
        if detailed_results:
            # Check for basic model information
            if 'model_info' in detailed_results:
                return True
            
            # Check for FBA analysis results
            if 'fba_analysis' in detailed_results:
                return True
            
            # Check for sensitivity analysis
            if 'sensitivity_analysis' in detailed_results:
                return True
        
        # Check data files
        if data_files:
            if 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
                analysis_data = data_files['analysis_results.json']
                if any(key in analysis_data for key in ['model_info', 'fba_analysis', 'sensitivity_analysis']):
                    return True
        
        return False
    
    def _has_fba_visualizations_data(self, experiment_result: Dict[str, Any]) -> bool:
        """Check if visualization data is available"""
        # Check for visualizations in experiment_result
        visualizations = experiment_result.get('visualizations', [])
        if visualizations:
            return True
        
        # Check for model name to scan directories
        model_name = experiment_result.get('model_name', '')
        if model_name:
            scanned_visualizations = self._scan_analysis_visualizations(model_name)
            if scanned_visualizations:
                return True
        
        return False
    
    def _has_fba_generated_reports_data(self, experiment_result: Dict[str, Any]) -> bool:
        """Check if generated reports data is available"""
        # Check for report files in experiment_result
        results = experiment_result.get('results', {})
        if results:
            data_files = results.get('data_files', {})
            if data_files:
                # Check for report files
                report_files = [f for f in data_files.keys() if 'report' in f.lower() or f.endswith('.txt')]
                if report_files:
                    return True
        
        # Check for model name to scan for report files
        model_name = experiment_result.get('model_name', '')
        if model_name:
            # Check for report files in analysis_results directory
            analysis_dir = os.path.join(os.path.dirname(__file__), 'analysis_results', model_name)
            if os.path.exists(analysis_dir):
                report_files = [f for f in os.listdir(analysis_dir) if f.endswith(('.txt', '.md', '.html'))]
                if report_files:
                    return True
        
        return False
    
    def _has_fba_strategic_recommendations_data(self, analysis_results: Dict[str, Any]) -> bool:
        """Check if strategic recommendations data is available"""
        results = analysis_results.get('results', {})
        if not results:
            return False
        
        detailed_results = results.get('results', {})
        data_files = results.get('data_files', {})
        
        # Check for recommendations in detailed results
        if detailed_results:
            if 'recommendations' in detailed_results:
                return True
            
            # Check for FBA results that could generate recommendations
            if 'fba_analysis' in detailed_results:
                fba_results = detailed_results['fba_analysis']
                if fba_results and fba_results.get('objective_value') is not None:
                    return True
        
        # Check data files
        if data_files:
            if 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
                analysis_data = data_files['analysis_results.json']
                if 'recommendations' in analysis_data:
                    return True
                
                # Check for FBA results
                if 'fba_analysis' in analysis_data:
                    fba_results = analysis_data['fba_analysis']
                    if fba_results and fba_results.get('objective_value') is not None:
                        return True
        
        return False

    def _display_fba_enhanced_header(self, experiment_result: Dict[str, Any]) -> None:
        """Display enhanced header with comprehensive information"""
        st.markdown("""
        # 🔬 Enhanced Flux Balance Analysis (FBA) Results
        
        ---
        """)
        
        # Create a comprehensive info panel
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Model", 
                experiment_result.get('model_name', 'Unknown'),
                help="Metabolic model analyzed"
            )
        
        with col2:
            st.metric(
                "Analysis Status", 
                "✅ Completed" if experiment_result.get('success') else "❌ Failed",
                help="Analysis completion status"
            )
        
        with col3:
            timestamp = experiment_result.get('experiment_timestamp', 'Unknown')
            st.metric(
                "Execution Time", 
                timestamp,
                help="When the analysis was performed"
            )
        
        with col4:
            # Calculate analysis duration if available
            duration = "N/A"
            if 'analysis_duration' in experiment_result:
                duration = f"{experiment_result['analysis_duration']:.1f}s"
            st.metric(
                "Duration", 
                duration,
                help="Analysis execution time"
            )
        
        st.markdown("---")
    
    def _display_fba_executive_summary(self, experiment_result: Dict[str, Any], analysis_results: Dict[str, Any]) -> None:
        """Display comprehensive executive summary for FBA analysis"""
        st.markdown("## 📊 Executive Summary")
        
        # Get summary data
        summary = analysis_results.get('summary', {})
        results = analysis_results.get('results', {})
        
        if not summary and not results:
            st.info("No summary information available")
            return
        
        # Extract data from results
        detailed_results = results.get('results', {})
        data_files = results.get('data_files', {})
        
        # Try to get model info from different sources
        model_info = None
        if 'model_info' in detailed_results:
            model_info = detailed_results['model_info']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            model_info = data_files['analysis_results.json'].get('model_info', {})
        
        # Try to get FBA results from different sources
        fba_results = None
        if 'fba_analysis' in detailed_results:
            fba_results = detailed_results['fba_analysis']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            fba_results = data_files['analysis_results.json'].get('fba_analysis', {})
        
        # Collect valid metrics
        valid_metrics = []
        
        # Check Growth Rate
        if fba_results and fba_results.get('objective_value') is not None:
            valid_metrics.append(('Growth Rate', f"{fba_results.get('objective_value', 0):.6f} h⁻¹", "Optimal growth rate from FBA"))
        
        # Check Solution Status
        if fba_results and fba_results.get('status'):
            status = fba_results.get('status', 'Unknown')
            valid_metrics.append(('Solution Status', status.title(), "FBA solution status"))
        
        # Check Reactions Count
        if model_info and model_info.get('reactions_count') is not None:
            reactions_count = model_info.get('reactions_count', 0)
            valid_metrics.append(('Reactions', f"{reactions_count:,}", "Total number of reactions in model"))
        
        # Check Metabolites Count
        if model_info and model_info.get('metabolites_count') is not None:
            metabolites_count = model_info.get('metabolites_count', 0)
            valid_metrics.append(('Metabolites', f"{metabolites_count:,}", "Total number of metabolites in model"))
        
        # Check Genes Count
        if model_info and model_info.get('genes_count') is not None:
            genes_count = model_info.get('genes_count', 0)
            valid_metrics.append(('Genes', f"{genes_count:,}", "Total number of genes in model"))
        
        # Check Non-zero Fluxes
        if fba_results and fba_results.get('flux_distribution'):
            flux_dist = fba_results.get('flux_distribution', {})
            non_zero_fluxes = sum(1 for flux in flux_dist.values() if abs(flux) > 1e-6)
            valid_metrics.append(('Non-zero Fluxes', f"{non_zero_fluxes:,}", "Number of reactions with non-zero flux"))
        
        # Check Model ID
        if model_info and model_info.get('model_id'):
            model_id = model_info.get('model_id', 'Unknown')
            valid_metrics.append(('Model ID', model_id, "Model identifier"))
        
        # If no valid metrics, show info message
        if not valid_metrics:
            st.info("📋 Analysis completed successfully. Executive summary data is being processed.")
            return
        
        # Display valid metrics in columns
        if len(valid_metrics) <= 4:
            # Use 4 columns for 4 or fewer metrics
            cols = st.columns(len(valid_metrics))
            for i, (title, value, help_text) in enumerate(valid_metrics):
                with cols[i]:
                    st.metric(title, value, help=help_text)
        else:
            # Use 4 columns for first row, then remaining columns for additional metrics
            first_row_metrics = valid_metrics[:4]
            remaining_metrics = valid_metrics[4:]
            
            # First row with 4 columns
            cols = st.columns(4)
            for i, (title, value, help_text) in enumerate(first_row_metrics):
                with cols[i]:
                    st.metric(title, value, help=help_text)
            
            # Remaining metrics in additional rows
            if remaining_metrics:
                remaining_cols = st.columns(len(remaining_metrics))
                for i, (title, value, help_text) in enumerate(remaining_metrics):
                    with remaining_cols[i]:
                        st.metric(title, value, help=help_text)
        
        # FBA results overview (only if we have FBA data)
        if fba_results:
            st.markdown("### 🔬 FBA Analysis Overview")
            
            # Collect overview metrics
            overview_metrics = []
            
            # Check for flux distribution
            if fba_results.get('flux_distribution'):
                flux_dist = fba_results.get('flux_distribution', {})
                non_zero_fluxes = sum(1 for flux in flux_dist.values() if abs(flux) > 1e-6)
                overview_metrics.append(('Non-zero Fluxes', f"{non_zero_fluxes:,}", "Number of reactions with non-zero flux"))
            
            # Check for model statistics
            if model_info:
                if model_info.get('genes_count') is not None:
                    genes_count = model_info.get('genes_count', 0)
                    overview_metrics.append(('Genes', f"{genes_count:,}", "Total number of genes in model"))
                
                if model_info.get('compartments_count') is not None:
                    compartments_count = model_info.get('compartments_count', 0)
                    overview_metrics.append(('Compartments', f"{compartments_count}", "Number of cellular compartments"))
            
            # Display overview metrics if available
            if overview_metrics:
                if len(overview_metrics) <= 3:
                    cols = st.columns(len(overview_metrics))
                    for i, (title, value, help_text) in enumerate(overview_metrics):
                        with cols[i]:
                            st.metric(title, value, help=help_text)
                else:
                    # First 3 metrics in first row
                    first_row = overview_metrics[:3]
                    cols = st.columns(3)
                    for i, (title, value, help_text) in enumerate(first_row):
                        with cols[i]:
                            st.metric(title, value, help=help_text)
                    
                    # Remaining metrics in second row
                    remaining = overview_metrics[3:]
                    if remaining:
                        remaining_cols = st.columns(len(remaining))
                        for i, (title, value, help_text) in enumerate(remaining):
                            with remaining_cols[i]:
                                st.metric(title, value, help=help_text)
    
    def _display_fba_detailed_analysis_results(self, analysis_results: Dict[str, Any]) -> None:
        """Display detailed FBA analysis results"""
        st.markdown("## 🔬 Detailed Analysis Results")
        
        # Get detailed results
        results = analysis_results.get('results', {})
        if not results:
            st.warning("⚠️ No detailed analysis results found")
            return
        
        detailed_results = results.get('results', {})
        data_files = results.get('data_files', {})
        
        # Display model information
        model_info = None
        if 'model_info' in detailed_results:
            model_info = detailed_results['model_info']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            model_info = data_files['analysis_results.json'].get('model_info', {})
        
        if model_info:
            st.markdown("### 📊 Model Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Model ID**: {model_info.get('model_id', 'Unknown')}")
                st.markdown(f"**Reactions**: {model_info.get('reactions_count', 0):,}")
                st.markdown(f"**Metabolites**: {model_info.get('metabolites_count', 0):,}")
            
            with col2:
                st.markdown(f"**Genes**: {model_info.get('genes_count', 0):,}")
                st.markdown(f"**Model Type**: Metabolic Network")
                st.markdown(f"**Analysis Type**: Flux Balance Analysis")
        
        # Display FBA results
        fba_results = None
        if 'fba_analysis' in detailed_results:
            fba_results = detailed_results['fba_analysis']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            fba_results = data_files['analysis_results.json'].get('fba_analysis', {})
        
        if fba_results:
            st.markdown("### 🔬 FBA Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                objective_value = fba_results.get('objective_value', 0)
                st.metric(
                    "Growth Rate",
                    f"{objective_value:.6f} h⁻¹",
                    help="Optimal growth rate"
                )
            
            with col2:
                status = fba_results.get('status', 'Unknown')
                st.metric(
                    "Solution Status",
                    status.title(),
                    help="FBA solution status"
                )
            
            # Flux distribution if available
            flux_dist = fba_results.get('flux_distribution', {})
            if flux_dist:
                st.markdown("### 🔄 Key Flux Distribution")
                
                # Convert to DataFrame for better display
                flux_data = []
                for reaction, flux in flux_dist.items():
                    if abs(flux) > 1e-6:  # Only show non-zero fluxes
                        flux_data.append({
                            'Reaction': reaction,
                            'Flux': flux
                        })
                
                if flux_data:
                    df_flux = pd.DataFrame(flux_data)
                    df_flux = df_flux.sort_values('Flux', key=abs, ascending=False)
                    
                    st.dataframe(
                        df_flux.head(20),
                        column_config={
                            "Flux": st.column_config.NumberColumn(
                                "Flux (mmol/g/h)",
                                format="%.6f"
                            )
                        },
                        hide_index=True
                    )
        
        # Display sensitivity analysis if available
        sensitivity_results = None
        if 'sensitivity_analysis' in detailed_results:
            sensitivity_results = detailed_results['sensitivity_analysis']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            sensitivity_results = data_files['analysis_results.json'].get('sensitivity_analysis', {})
        
        if sensitivity_results:
            st.markdown("### 📊 Sensitivity Analysis")
            
            # Glucose sensitivity
            glucose_sens = sensitivity_results.get('glucose_sensitivity', {})
            if glucose_sens:
                st.markdown("#### 🌱 Glucose Sensitivity")
                
                glucose_data = []
                for rate, growth in glucose_sens.items():
                    glucose_data.append({
                        'Glucose Rate (mmol/g/h)': float(rate),
                        'Growth Rate (h⁻¹)': growth
                    })
                
                if glucose_data:
                    df_glucose = pd.DataFrame(glucose_data)
                    
                    fig = px.line(
                        df_glucose,
                        x='Glucose Rate (mmol/g/h)',
                        y='Growth Rate (h⁻¹)',
                        title="Growth Rate vs Glucose Uptake Rate",
                        markers=True
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Oxygen sensitivity
            oxygen_sens = sensitivity_results.get('oxygen_sensitivity', {})
            if oxygen_sens:
                st.markdown("#### 💨 Oxygen Sensitivity")
                
                oxygen_data = []
                for rate, growth in oxygen_sens.items():
                    oxygen_data.append({
                        'Oxygen Rate (mmol/g/h)': float(rate),
                        'Growth Rate (h⁻¹)': growth
                    })
                
                if oxygen_data:
                    df_oxygen = pd.DataFrame(oxygen_data)
                    
                    fig = px.line(
                        df_oxygen,
                        x='Oxygen Rate (mmol/g/h)',
                        y='Growth Rate (h⁻¹)',
                        title="Growth Rate vs Oxygen Availability",
                        markers=True
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Anaerobic growth
            anaerobic_growth = sensitivity_results.get('anaerobic_growth', 0)
            if anaerobic_growth > 0:
                st.markdown("#### 🌬️ Anaerobic Growth")
                st.metric(
                    "Anaerobic Growth Rate",
                    f"{anaerobic_growth:.6f} h⁻¹",
                    help="Growth rate under anaerobic conditions"
                )
        
        # Display pathway analysis if available
        pathway_results = None
        if 'pathway_analysis' in detailed_results:
            pathway_results = detailed_results['pathway_analysis']
        elif 'analysis_results.json' in data_files and isinstance(data_files['analysis_results.json'], dict):
            pathway_results = data_files['analysis_results.json'].get('pathway_analysis', {})
        
        if pathway_results:
            pathway_dist = pathway_results.get('pathway_distribution', {})
            if pathway_dist:
                st.markdown("### 🧬 Pathway Analysis")
                
                pathway_data = []
                for pathway, count in pathway_dist.items():
                    pathway_data.append({
                        'Pathway': pathway,
                        'Reaction Count': count
                    })
                
                if pathway_data:
                    df_pathway = pd.DataFrame(pathway_data)
                    
                    fig = px.pie(
                        df_pathway,
                        values='Reaction Count',
                        names='Pathway',
                        title="Reaction Distribution by Pathway"
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

    def _display_fba_generated_reports(self, experiment_result: Dict[str, Any]) -> None:
        """Display generated reports for FBA analysis"""
        st.markdown("## 📋 Generated Reports")
        
        # Get report information from analysis results
        analysis_results = experiment_result.get('results', {})
        results = analysis_results.get('results', {})
        
        # Check for generated files
        output_directory = analysis_results.get('output_directory', '')
        files_generated = results.get('files_generated', [])
        data_files = results.get('data_files', {})
        
        # Check for LLM generated report in experiment_result
        llm_report = experiment_result.get('report', '')
        
        # Check for report files in ResultsData directory
        model_name = experiment_result.get('model_name', '')
        results_data_dir = os.path.join(os.path.dirname(__file__), 'ResultsData')
        report_files = []
        
        if model_name and os.path.exists(results_data_dir):
            for file in os.listdir(results_data_dir):
                if file.startswith(f'fba_analysis_report_{model_name}') and file.endswith('.txt'):
                    report_files.append(os.path.join(results_data_dir, file))
        
        # If no reports found in any location, show default content
        if not files_generated and not data_files and not llm_report and not report_files:
            st.info("📋 Analysis completed successfully. Reports are being generated...")
            
            # Provide default report information
            st.markdown("### 📄 Expected Reports")
            st.markdown("""
            The FBA analysis typically generates the following reports:
            
            **1. Comprehensive Analysis Report**
            - Executive summary of findings
            - Model overview and statistics
            - Key experimental findings
            - Growth rate analysis
            - Flux distribution analysis
            - Sensitivity analysis results
            
            **2. Data Files**
            - Flux distribution data (CSV)
            - Sensitivity analysis data (CSV)
            - Model statistics (JSON)
            - Analysis summary (JSON)
            
            **3. Visualization Files**
            - Growth rate charts
            - Flux distribution plots
            - Sensitivity analysis graphs
            """)
            return
        
        # Display report summary
        col1, col2, col3 = st.columns(3)
        
        total_files = len(files_generated) + len(report_files)
        if llm_report:
            total_files += 1
        
        with col1:
            st.metric("Total Files", total_files)
        
        with col2:
            if output_directory and os.path.exists(output_directory):
                total_size = sum(os.path.getsize(os.path.join(output_directory, f)) 
                               for f in os.listdir(output_directory) 
                               if os.path.isfile(os.path.join(output_directory, f)))
                st.metric("Total Size", f"{total_size / (1024*1024):.2f} MB")
            else:
                st.metric("Total Size", "N/A")
        
        with col3:
            if output_directory and os.path.exists(output_directory):
                available_files = len([f for f in os.listdir(output_directory) 
                                     if os.path.isfile(os.path.join(output_directory, f))])
                st.metric("Available", available_files)
            else:
                st.metric("Available", len(report_files))
        
        # Display LLM generated report
        if llm_report:
            st.markdown("### 🤖 LLM Generated Report")
            with st.expander("📄 Comprehensive FBA Analysis Report", expanded=True):
                st.markdown(llm_report)
        
        # Display report files from ResultsData
        if report_files:
            st.markdown("### 📄 Analysis Report Files")
            for report_file in report_files:
                with st.expander(f"📄 {os.path.basename(report_file)}", expanded=False):
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        # Display file info
                        file_size = os.path.getsize(report_file)
                        file_size_mb = file_size / (1024 * 1024)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("File Size", f"{file_size_mb:.2f} MB")
                        
                        with col2:
                            st.metric("File Type", "TXT")
                        
                        with col3:
                            st.metric("Status", "✅ Available")
                        
                        # Display content
                        st.text_area("Report Content", report_content, height=400)
                        
                    except Exception as e:
                        st.error(f"Error reading report file: {e}")
        
        # Display individual files from output directory
        if output_directory and os.path.exists(output_directory):
            st.markdown("### 📄 Generated Files")
            
            for file in os.listdir(output_directory):
                file_path = os.path.join(output_directory, file)
                if os.path.isfile(file_path):
                    with st.expander(f"📄 {file}", expanded=False):
                        # Get file info
                        file_size = os.path.getsize(file_path)
                        file_size_mb = file_size / (1024 * 1024)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("File Size", f"{file_size_mb:.2f} MB")
                        
                        with col2:
                            st.metric("File Type", os.path.splitext(file)[1].upper())
                        
                        with col3:
                            st.metric("Status", "✅ Available")
                        
                        # Display file content if it's a text file
                        if file.endswith('.txt') or file.endswith('.md'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    file_content = f.read()
                                st.text_area("File Content", file_content, height=300)
                            except Exception as e:
                                st.error(f"Error reading file: {e}")
                        elif file.endswith('.json'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    json_content = json.load(f)
                                st.json(json_content)
                            except Exception as e:
                                st.error(f"Error reading JSON file: {e}")
                        elif file.endswith('.csv'):
                            try:
                                import pandas as pd
                                df = pd.read_csv(file_path)
                                st.dataframe(df, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error reading CSV file: {e}")
                        elif file.endswith('.html'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                st.components.v1.html(html_content, height=600)
                            except Exception as e:
                                st.error(f"Error reading HTML file: {e}")
                        elif file.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                            st.image(file_path, caption=file)
        
        # Display data files from results
        if data_files:
            st.markdown("### 📊 Analysis Data Files")
            
            for file_name, data in data_files.items():
                with st.expander(f"📊 {file_name}", expanded=False):
                    if isinstance(data, dict):
                        st.json(data)
                    elif isinstance(data, str):
                        st.text_area("File Content", data, height=200)
                    else:
                        st.write(data)
    
    def _display_fba_strategic_recommendations(self, analysis_results: Dict[str, Any]) -> None:
        """Display strategic recommendations for FBA analysis"""
        st.markdown("## 🎯 Strategic Recommendations")
        
        # Get analysis data
        results = analysis_results.get('results', {})
        summary = analysis_results.get('summary', {})
        
        # Generate recommendations based on FBA results
        recommendations = []
        
        # Based on growth rate
        if 'fba_summary' in summary:
            fba_summary = summary['fba_summary']
            growth_rate = fba_summary.get('growth_rate', 0)
            
            if growth_rate > 0.5:
                recommendations.append("• **High growth potential** - Consider optimizing for biomass production")
                recommendations.append("• **Efficient metabolism** - Model shows good metabolic efficiency")
            elif growth_rate > 0.1:
                recommendations.append("• **Moderate growth rate** - Room for optimization through media design")
                recommendations.append("• **Balanced metabolism** - Consider nutrient supplementation")
            else:
                recommendations.append("• **Low growth rate** - Investigate metabolic bottlenecks")
                recommendations.append("• **Optimization needed** - Focus on essential nutrient supply")
        
        # Based on sensitivity analysis
        if 'sensitivity_analysis' in results:
            sensitivity = results['sensitivity_analysis']
            
            if 'glucose_sensitivity' in sensitivity:
                recommendations.append("• **Glucose sensitivity analyzed** - Use results for media optimization")
            
            if 'oxygen_sensitivity' in sensitivity:
                recommendations.append("• **Oxygen sensitivity analyzed** - Consider aeration strategies")
        
        # General FBA recommendations
        recommendations.extend([
            "• **Validate predictions** with experimental growth rate measurements",
            "• **Optimize culture conditions** based on sensitivity analysis results",
            "• **Monitor metabolite levels** to verify flux predictions",
            "• **Consider scale-up implications** of predicted growth rates",
            "• **Use flux analysis** for metabolic engineering decisions"
        ])
        
        # Display recommendations
        for recommendation in recommendations:
            st.markdown(recommendation)
        
        # Add next steps
        st.markdown("### 🚀 Next Steps")
        st.markdown("""
        1. **Experimental Validation**: Compare predicted growth rates with actual measurements
        2. **Media Optimization**: Use sensitivity analysis to design optimal growth media
        3. **Flux Verification**: Measure key metabolite fluxes to validate predictions
        4. **Process Scale-up**: Apply insights to larger-scale fermentation processes
        5. **Continuous Monitoring**: Implement real-time monitoring of growth and metabolism
        """)

    def _display_fba_visualizations(self, experiment_result: Dict[str, Any]) -> None:
        """Display FBA visualizations"""
        st.markdown("## 📈 Generated Visualizations")
        
        # First try to get visualizations from experiment_result
        visualizations = experiment_result.get('visualizations', [])
        
        # If no visualizations in experiment_result, scan the analysis_results directory
        if not visualizations:
            model_name = experiment_result.get('model_name', '')
            if model_name:
                visualizations = self._scan_analysis_visualizations(model_name)
        
        if not visualizations:
            st.info("No visualizations available")
            return
        
        # Ensure visualizations is a list and handle both string and dict items
        if not isinstance(visualizations, list):
            visualizations = [visualizations]
        
        # Filter and convert visualizations to proper format
        processed_visualizations = []
        for viz in visualizations:
            if isinstance(viz, str):
                # Convert string to dict format
                processed_visualizations.append({
                    'name': os.path.basename(viz),
                    'path': viz,
                    'type': 'image' if viz.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')) else 'html'
                })
            elif isinstance(viz, dict):
                processed_visualizations.append(viz)
        
        # Group visualizations by type
        image_files = [v for v in processed_visualizations if v.get('type') == 'image']
        html_files = [v for v in processed_visualizations if v.get('type') == 'html']
        
        # Display interactive HTML visualizations
        if html_files:
            st.markdown("### 🖱️ Interactive Visualizations")
            
            for viz in html_files:
                with st.expander(f"📊 {viz.get('name', 'Unknown')}", expanded=True):
                    try:
                        # Read and display HTML content
                        if os.path.exists(viz.get('path', '')):
                            with open(viz.get('path', ''), 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            st.components.v1.html(html_content, height=600)
                        else:
                            st.warning(f"File not found: {viz.get('path', '')}")
                    except Exception as e:
                        st.error(f"Error displaying visualization: {e}")
        
        # Display static image visualizations
        if image_files:
            st.markdown("### 📷 Static Visualizations")
            
            for viz in image_files:
                with st.expander(f"📷 {viz.get('name', 'Unknown')}", expanded=True):
                    try:
                        if os.path.exists(viz.get('path', '')):
                            st.image(viz.get('path', ''), use_container_width=True)
                        else:
                            st.warning(f"File not found: {viz.get('path', '')}")
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
        
        # Visualization summary
        st.markdown("### 📊 Visualization Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", len(processed_visualizations))
        
        with col2:
            st.metric("Interactive", len(html_files))
        
        with col3:
            st.metric("Static Images", len(image_files))
        
        # Create interactive charts from data if available
        results = experiment_result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                
                if 'analysis_results.json' in data_files:
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        
                        # Create glucose sensitivity chart
                        sensitivity_analysis = model_info.get('sensitivity_analysis', {})
                        glucose_sensitivity = sensitivity_analysis.get('glucose_sensitivity', {})
                        if glucose_sensitivity:
                            st.markdown("### 🌱 Glucose Sensitivity Chart")
                            
                            glucose_data = []
                            for rate, growth in glucose_sensitivity.items():
                                glucose_data.append({
                                    'Glucose Rate (mmol/g/h)': rate,
                                    'Growth Rate (h⁻¹)': growth
                                })
                            
                            if glucose_data:
                                df_glucose = pd.DataFrame(glucose_data)
                                
                                fig = px.line(
                                    df_glucose,
                                    x='Glucose Rate (mmol/g/h)',
                                    y='Growth Rate (h⁻¹)',
                                    title="Growth Rate vs Glucose Uptake Rate",
                                    markers=True
                                )
                                
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Create oxygen sensitivity chart
                        oxygen_sensitivity = sensitivity_analysis.get('oxygen_sensitivity', {})
                        if oxygen_sensitivity:
                            st.markdown("### 💨 Oxygen Sensitivity Chart")
                            
                            oxygen_data = []
                            for rate, growth in oxygen_sensitivity.items():
                                oxygen_data.append({
                                    'Oxygen Rate (mmol/g/h)': rate,
                                    'Growth Rate (h⁻¹)': growth
                                })
                            
                            if oxygen_data:
                                df_oxygen = pd.DataFrame(oxygen_data)
                                
                                fig = px.line(
                                    df_oxygen,
                                    x='Oxygen Rate (mmol/g/h)',
                                    y='Growth Rate (h⁻¹)',
                                    title="Growth Rate vs Oxygen Availability",
                                    markers=True
                                )
                                
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)

    def _display_fba_report(self, experiment_result: Dict[str, Any]) -> None:
        """Display FBA analysis report"""
        st.markdown("## 📋 Analysis Report")
        
        # Display the generated report
        report = experiment_result.get('report', '')
        
        if report:
            st.markdown(report)
        else:
            st.info("📝 No report generated")
        
        # Display summary from text file if available
        results = experiment_result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                
                if 'analysis_summary.txt' in data_files:
                    summary_text = data_files['analysis_summary.txt']
                    if isinstance(summary_text, str):
                        st.markdown("### 📄 Analysis Summary")
                        st.text(summary_text)

    def _display_constraint_based_summary(self, experiment_result: Dict[str, Any]) -> None:
        """Display summary of Constraint-Based Analysis results"""
        st.markdown("## 📊 Executive Summary")
        
        # Basic information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Model Name",
                experiment_result.get('model_name', 'Unknown')
            )
        
        with col2:
            st.metric(
                "Analysis Type",
                "Constraint-Based Analysis"
            )
        
        with col3:
            st.metric(
                "Status",
                "✅ Completed" if experiment_result.get('success', False) else "❌ Failed"
            )
        
        # Display key results if available
        results = experiment_result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                
                # Display basic model information
                if 'analysis_results.json' in data_files:
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        basic_info = model_info.get('basic_info', {})
                        if basic_info:
                            st.markdown("### 📋 Model Information")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Reactions", basic_info.get('reactions_count', 0))
                            
                            with col2:
                                st.metric("Metabolites", basic_info.get('metabolites_count', 0))
                            
                            with col3:
                                st.metric("Genes", basic_info.get('genes_count', 0))
                
                # Display FBA results
                if 'analysis_results.json' in data_files:
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        fba_analysis = model_info.get('fba_analysis', {})
                        if fba_analysis:
                            st.markdown("### 🔬 FBA Results")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric(
                                    "Growth Rate",
                                    f"{fba_analysis.get('objective_value', 0):.6f} h⁻¹"
                                )
                            
                            with col2:
                                st.metric(
                                    "Status",
                                    fba_analysis.get('status', 'Unknown')
                                )

    def _display_constraint_based_analysis_results(self, experiment_result: Dict[str, Any]) -> None:
        """Display detailed Constraint-Based Analysis results"""
        st.markdown("## 🔬 Detailed Analysis Results")
        
        results = experiment_result.get('results', {})
        if not results:
            st.warning("⚠️ No analysis results found")
            return
        
        analysis_results = results.get('results', {})
        if not analysis_results:
            st.warning("⚠️ No detailed analysis results found")
            return
        
        data_files = analysis_results.get('data_files', {})
        
        # Display analysis results from JSON file
        if 'analysis_results.json' in data_files:
            model_info = data_files['analysis_results.json']
            if isinstance(model_info, dict):
                
                # Growth Analysis
                growth_analysis = model_info.get('growth_analysis', {})
                if growth_analysis:
                    st.markdown("### 🌱 Growth Capabilities")
                    
                    # Carbon source growth
                    carbon_growth = growth_analysis.get('carbon_source_growth', {})
                    if carbon_growth:
                        st.markdown("**Carbon Source Utilization:**")
                        carbon_data = []
                        for source, rate in carbon_growth.items():
                            carbon_data.append({
                                'Carbon Source': source,
                                'Growth Rate (h⁻¹)': rate
                            })
                        
                        if carbon_data:
                            df_carbon = pd.DataFrame(carbon_data)
                            st.dataframe(df_carbon, use_container_width=True)
                    
                    # Aerobic vs Anaerobic
                    aerobic_growth = growth_analysis.get('aerobic_growth', 0)
                    anaerobic_growth = growth_analysis.get('anaerobic_growth', 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Aerobic Growth", f"{aerobic_growth:.6f} h⁻¹")
                    with col2:
                        st.metric("Anaerobic Growth", f"{anaerobic_growth:.6f} h⁻¹")
                    with col3:
                        if aerobic_growth > 0:
                            reduction = ((aerobic_growth - anaerobic_growth) / aerobic_growth * 100)
                            st.metric("Growth Reduction", f"{reduction:.1f}%")
                
                # Environmental Analysis
                environmental_analysis = model_info.get('environmental_analysis', {})
                if environmental_analysis:
                    st.markdown("### 🌡️ Environmental Conditions")
                    
                    # pH analysis
                    ph_analysis = environmental_analysis.get('ph_analysis', {})
                    if ph_analysis:
                        st.markdown("**pH Effects:**")
                        ph_data = []
                        for condition, data in ph_analysis.items():
                            if isinstance(data, dict):
                                ph_data.append({
                                    'pH Condition': condition,
                                    'Growth Rate (h⁻¹)': data.get('growth_rate', 0),
                                    'Status': data.get('status', 'Unknown')
                                })
                        
                        if ph_data:
                            df_ph = pd.DataFrame(ph_data)
                            st.dataframe(df_ph, use_container_width=True)
                    
                    # Temperature analysis
                    temp_analysis = environmental_analysis.get('temperature_analysis', {})
                    if temp_analysis:
                        st.markdown("**Temperature Effects:**")
                        temp_data = []
                        for condition, data in temp_analysis.items():
                            if isinstance(data, dict):
                                temp_data.append({
                                    'Temperature': condition,
                                    'Growth Rate (h⁻¹)': data.get('growth_rate', 0),
                                    'Status': data.get('status', 'Unknown')
                                })
                        
                        if temp_data:
                            df_temp = pd.DataFrame(temp_data)
                            st.dataframe(df_temp, use_container_width=True)
                
                # Essentiality Analysis
                essentiality_analysis = model_info.get('essentiality_analysis', {})
                if essentiality_analysis:
                    st.markdown("### 🧬 Essential Reactions")
                    
                    essential_reactions = essentiality_analysis.get('essential_reactions', [])
                    total_tested = essentiality_analysis.get('total_tested', 0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Tested", total_tested)
                    with col2:
                        st.metric("Essential Found", len(essential_reactions))
                    
                    if essential_reactions:
                        st.markdown("**Essential Reactions:**")
                        for reaction in essential_reactions:
                            st.markdown(f"- **{reaction}**")
                    
                    # Reaction analysis details
                    reaction_analysis = essentiality_analysis.get('reaction_analysis', {})
                    if reaction_analysis:
                        st.markdown("**Reaction Analysis Details:**")
                        reaction_data = []
                        for reaction, data in reaction_analysis.items():
                            if isinstance(data, dict):
                                reaction_data.append({
                                    'Reaction': reaction,
                                    'Wild-type Flux': data.get('wild_type_flux', 0),
                                    'Knockout Growth': data.get('knockout_growth', 0),
                                    'Essential': 'Yes' if data.get('is_essential', False) else 'No'
                                })
                        
                        if reaction_data:
                            df_reactions = pd.DataFrame(reaction_data)
                            st.dataframe(df_reactions, use_container_width=True)

    def _display_constraint_based_visualizations(self, experiment_result: Dict[str, Any]) -> None:
        """Display constraint-based analysis visualizations"""
        st.markdown("## 📈 Generated Visualizations")
        
        # First try to get visualizations from experiment_result
        visualizations = experiment_result.get('visualizations', [])
        
        # If no visualizations in experiment_result, scan the analysis_results directory
        if not visualizations:
            model_name = experiment_result.get('model_name', '')
            if model_name:
                visualizations = self._scan_analysis_visualizations(model_name)
        
        if not visualizations:
            st.info("No visualizations available")
            return
        
        # Ensure visualizations is a list and handle both string and dict items
        if not isinstance(visualizations, list):
            visualizations = [visualizations]
        
        # Filter and convert visualizations to proper format
        processed_visualizations = []
        for viz in visualizations:
            if isinstance(viz, str):
                # Convert string to dict format
                processed_visualizations.append({
                    'name': os.path.basename(viz),
                    'path': viz,
                    'type': 'image' if viz.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')) else 'html'
                })
            elif isinstance(viz, dict):
                processed_visualizations.append(viz)
        
        # Group visualizations by type
        image_files = [v for v in processed_visualizations if v.get('type') == 'image']
        html_files = [v for v in processed_visualizations if v.get('type') == 'html']
        
        # Display interactive HTML visualizations
        if html_files:
            st.markdown("### 🖱️ Interactive Visualizations")
            
            for viz in html_files:
                with st.expander(f"📊 {viz.get('name', 'Unknown')}", expanded=True):
                    try:
                        # Read and display HTML content
                        if os.path.exists(viz.get('path', '')):
                            with open(viz.get('path', ''), 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            st.components.v1.html(html_content, height=600)
                        else:
                            st.warning(f"File not found: {viz.get('path', '')}")
                    except Exception as e:
                        st.error(f"Error displaying visualization: {e}")
        
        # Display static image visualizations
        if image_files:
            st.markdown("### 📷 Static Visualizations")
            
            for viz in image_files:
                with st.expander(f"📷 {viz.get('name', 'Unknown')}", expanded=True):
                    try:
                        if os.path.exists(viz.get('path', '')):
                            st.image(viz.get('path', ''), use_container_width=True)
                        else:
                            st.warning(f"File not found: {viz.get('path', '')}")
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
        
        # Visualization summary
        st.markdown("### 📊 Visualization Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", len(processed_visualizations))
        
        with col2:
            st.metric("Interactive", len(html_files))
        
        with col3:
            st.metric("Static Images", len(image_files))
        
        # Create interactive charts from data if available
        results = experiment_result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                
                if 'analysis_results.json' in data_files:
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        
                        # Create carbon source growth chart
                        growth_analysis = model_info.get('growth_analysis', {})
                        carbon_growth = growth_analysis.get('carbon_source_growth', {})
                        if carbon_growth:
                            st.markdown("### 🌱 Carbon Source Growth Chart")
                            
                            carbon_data = []
                            for source, rate in carbon_growth.items():
                                carbon_data.append({
                                    'Carbon Source': source,
                                    'Growth Rate (h⁻¹)': rate
                                })
                            
                            if carbon_data:
                                df_carbon = pd.DataFrame(carbon_data)
                                
                                fig = px.bar(
                                    df_carbon,
                                    x='Carbon Source',
                                    y='Growth Rate (h⁻¹)',
                                    title="Growth Rates on Different Carbon Sources",
                                    color='Growth Rate (h⁻¹)',
                                    color_continuous_scale='viridis'
                                )
                                
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Create environmental conditions chart
                        environmental_analysis = model_info.get('environmental_analysis', {})
                        ph_analysis = environmental_analysis.get('ph_analysis', {})
                        if ph_analysis:
                            st.markdown("### 🌡️ pH Sensitivity Chart")
                            
                            ph_data = []
                            for ph, rate in ph_analysis.items():
                                ph_data.append({
                                    'pH': float(ph),
                                    'Growth Rate (h⁻¹)': rate
                                })
                            
                            if ph_data:
                                df_ph = pd.DataFrame(ph_data)
                                df_ph = df_ph.sort_values('pH')
                                
                                fig = px.line(
                                    df_ph,
                                    x='pH',
                                    y='Growth Rate (h⁻¹)',
                                    title="Growth Rate vs pH",
                                    markers=True
                                )
                                
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Create essentiality analysis chart
                        essentiality_analysis = model_info.get('essentiality_analysis', {})
                        essential_genes = essentiality_analysis.get('essential_genes', [])
                        if essential_genes:
                            st.markdown("### 🧬 Essential Genes Analysis")
                            
                            essential_data = []
                            for gene in essential_genes:
                                essential_data.append({
                                    'Gene': gene,
                                    'Status': 'Essential'
                                })
                            
                            if essential_data:
                                df_essential = pd.DataFrame(essential_data)
                                
                                fig = px.bar(
                                    df_essential,
                                    x='Gene',
                                    y='Status',
                                    title="Essential Genes",
                                    color='Status',
                                    color_discrete_map={'Essential': 'red'}
                                )
                                
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)

    def _display_constraint_based_report(self, experiment_result: Dict[str, Any]) -> None:
        """Display Constraint-Based Analysis report"""
        st.markdown("## 📋 Analysis Report")
        
        # Display the generated report
        report = experiment_result.get('report', '')
        
        if report:
            st.markdown(report)
        else:
            st.info("📝 No report generated")
        
        # Display summary from text file if available
        results = experiment_result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                
                if 'analysis_summary.txt' in data_files:
                    summary_text = data_files['analysis_summary.txt']
                    if isinstance(summary_text, str):
                        st.markdown("### 📄 Analysis Summary")
                        st.text(summary_text)

    def _display_fba_summary(self, experiment_result: Dict[str, Any]) -> None:
        """Display summary of FBA results"""
        st.markdown("## 📊 Executive Summary")
        
        # Basic information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Model Name",
                experiment_result.get('model_name', 'Unknown')
            )
        
        with col2:
            st.metric(
                "Analysis Type",
                "Flux Balance Analysis (FBA)"
            )
        
        with col3:
            st.metric(
                "Status",
                "✅ Completed" if experiment_result.get('success', False) else "❌ Failed"
            )
        
        # Display key results if available
        results = experiment_result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                
                # Display basic model information
                if 'analysis_results.json' in data_files:
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        basic_info = model_info.get('basic_info', {})
                        if basic_info:
                            st.markdown("### 📋 Model Information")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Reactions", basic_info.get('reactions_count', 0))
                            
                            with col2:
                                st.metric("Metabolites", basic_info.get('metabolites_count', 0))
                            
                            with col3:
                                st.metric("Genes", basic_info.get('genes_count', 0))
                
                # Display FBA results
                if 'analysis_results.json' in data_files:
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        fba_analysis = model_info.get('fba_analysis', {})
                        if fba_analysis:
                            st.markdown("### 🔬 FBA Results")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric(
                                    "Growth Rate",
                                    f"{fba_analysis.get('objective_value', 0):.6f} h⁻¹"
                                )
                            
                            with col2:
                                st.metric(
                                    "Status",
                                    fba_analysis.get('status', 'Unknown')
                                )

    def _display_fba_analysis_results(self, experiment_result: Dict[str, Any]) -> None:
        """Display detailed FBA analysis results"""
        st.markdown("## 🔬 Detailed Analysis Results")
        
        results = experiment_result.get('results', {})
        if not results:
            st.warning("⚠️ No analysis results found")
            return
        
        analysis_results = results.get('results', {})
        if not analysis_results:
            st.warning("⚠️ No detailed analysis results found")
            return
        
        data_files = analysis_results.get('data_files', {})
        
        # Display analysis results from JSON file
        if 'analysis_results.json' in data_files:
            model_info = data_files['analysis_results.json']
            if isinstance(model_info, dict):
                
                # FBA Analysis
                fba_analysis = model_info.get('fba_analysis', {})
                if fba_analysis:
                    st.markdown("### 🔬 Flux Balance Analysis")
                    
                    # Basic FBA results
                    objective_value = fba_analysis.get('objective_value', 0)
                    status = fba_analysis.get('status', 'Unknown')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Objective Value", f"{objective_value:.6f}")
                    with col2:
                        st.metric("Solution Status", status)
                    
                    # Flux distribution
                    flux_distribution = fba_analysis.get('flux_distribution', {})
                    if flux_distribution:
                        st.markdown("**Top Active Reactions:**")
                        flux_data = []
                        for reaction, flux in flux_distribution.items():
                            if abs(flux) > 0.001:  # Only show significant fluxes
                                flux_data.append({
                                    'Reaction': reaction,
                                    'Flux': flux
                                })
                        
                        if flux_data:
                            # Sort by absolute flux value
                            flux_data.sort(key=lambda x: abs(x['Flux']), reverse=True)
                            df_flux = pd.DataFrame(flux_data[:20])  # Show top 20
                            st.dataframe(df_flux, use_container_width=True)
                
                # Sensitivity Analysis
                sensitivity_analysis = model_info.get('sensitivity_analysis', {})
                if sensitivity_analysis:
                    st.markdown("### 📊 Sensitivity Analysis")
                    
                    # Glucose sensitivity
                    glucose_sensitivity = sensitivity_analysis.get('glucose_sensitivity', {})
                    if glucose_sensitivity:
                        st.markdown("**Glucose Uptake Sensitivity:**")
                        glucose_data = []
                        for rate, growth in glucose_sensitivity.items():
                            glucose_data.append({
                                'Glucose Rate (mmol/g/h)': rate,
                                'Growth Rate (h⁻¹)': growth
                            })
                        
                        if glucose_data:
                            df_glucose = pd.DataFrame(glucose_data)
                            st.dataframe(df_glucose, use_container_width=True)
                    
                    # Oxygen sensitivity
                    oxygen_sensitivity = sensitivity_analysis.get('oxygen_sensitivity', {})
                    if oxygen_sensitivity:
                        st.markdown("**Oxygen Availability Sensitivity:**")
                        oxygen_data = []
                        for rate, growth in oxygen_sensitivity.items():
                            oxygen_data.append({
                                'Oxygen Rate (mmol/g/h)': rate,
                                'Growth Rate (h⁻¹)': growth
                            })
                        
                        if oxygen_data:
                            df_oxygen = pd.DataFrame(oxygen_data)
                            st.dataframe(df_oxygen, use_container_width=True)
                
                # Pathway Analysis
                pathway_analysis = model_info.get('pathway_analysis', {})
                if pathway_analysis:
                    st.markdown("### 🧬 Pathway Analysis")
                    
                    pathway_distribution = pathway_analysis.get('pathway_distribution', {})
                    if pathway_distribution:
                        st.markdown("**Metabolic Pathway Distribution:**")
                        pathway_data = []
                        for pathway, count in pathway_distribution.items():
                            pathway_data.append({
                                'Pathway': pathway,
                                'Reaction Count': count
                            })
                        
                        if pathway_data:
                            df_pathway = pd.DataFrame(pathway_data)
                            st.dataframe(df_pathway, use_container_width=True)

    def _scan_analysis_visualizations(self, model_name: str) -> List[Dict[str, str]]:
        """
        Scan analysis results directory for visualization files
        
        Args:
            model_name (str): Name of the model
            
        Returns:
            List of visualization file information
        """
        visualizations = []
        
        try:
            # Look in analysis_results directory
            analysis_dir = os.path.join(os.path.dirname(__file__), 'analysis_results', model_name)
            if os.path.exists(analysis_dir):
                # Look for image files
                image_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.pdf']
                for file in os.listdir(analysis_dir):
                    file_path = os.path.join(analysis_dir, file)
                    if os.path.isfile(file_path):
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext in image_extensions:
                            visualizations.append({
                                'name': file,
                                'path': file_path,
                                'type': 'image',
                                'size': os.path.getsize(file_path)
                            })
                
                # Look for HTML files
                for file in os.listdir(analysis_dir):
                    file_path = os.path.join(analysis_dir, file)
                    if os.path.isfile(file_path) and file.endswith('.html'):
                        visualizations.append({
                            'name': file,
                            'path': file_path,
                            'type': 'html',
                            'size': os.path.getsize(file_path)
                        })
            
            # Also look in model_data directory
            model_data_dir = os.path.join(os.path.dirname(__file__), 'model_data', model_name)
            if os.path.exists(model_data_dir):
                # Look for visualizations subdirectory
                viz_dir = os.path.join(model_data_dir, 'visualizations')
                if os.path.exists(viz_dir):
                    for file in os.listdir(viz_dir):
                        file_path = os.path.join(viz_dir, file)
                        if os.path.isfile(file_path):
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']:
                                visualizations.append({
                                    'name': file,
                                    'path': file_path,
                                    'type': 'image',
                                    'size': os.path.getsize(file_path)
                                })
                            elif file_ext == '.html':
                                visualizations.append({
                                    'name': file,
                                    'path': file_path,
                                    'type': 'html',
                                    'size': os.path.getsize(file_path)
                                })
                
                # Look for analysis_report.html in model_data directory
                report_file = os.path.join(model_data_dir, 'analysis_report.html')
                if os.path.exists(report_file):
                    visualizations.append({
                        'name': 'analysis_report.html',
                        'path': report_file,
                        'type': 'html',
                        'size': os.path.getsize(report_file)
                    })
            
            print(f"📊 Found {len(visualizations)} visualization files for {model_name}")
            return visualizations
            
        except Exception as e:
            print(f"⚠️ Error scanning visualizations for {model_name}: {e}")
            return []

# Global instance for easy access
enhanced_visualizer = EnhancedResultVisualizer()

# Backward compatibility
ResultVisualizer = EnhancedResultVisualizer
visualize_gene_deletion_results = enhanced_visualizer.visualize_gene_deletion_results_enhanced

def get_result_visualizer():
    """Get the global result visualizer instance for backward compatibility"""
    return enhanced_visualizer
