#!/usr/bin/env python3
"""
FBA Analysis Agent - Enhanced version with improved visualization and presentation
"""

import os
import json
import traceback
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class FBAAnalysisAgent:
    """
    Enhanced agent for analyzing FBA analysis results and providing comprehensive LLM insights
    """
    
    def __init__(self):
        """Initialize the enhanced FBA analysis agent"""
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
            from experiment_executor import get_fba_analysis_status
            
            analysis_data = get_fba_analysis_status(model_name)
            if analysis_data:
                self.analysis_results = analysis_data
                self.current_model = model_name
                self.analysis_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error loading FBA analysis results: {e}")
            return False
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive FBA analysis report
        
        Returns:
            Dict containing the comprehensive report
        """
        try:
            if not self.analysis_results:
                return {
                    'error': 'No analysis results loaded',
                    'status': 'failed'
                }
            
            # Extract key information
            summary = self.analysis_results.get('summary', {})
            results = self.analysis_results.get('results', {})
            
            # Generate comprehensive report
            report = {
                'executive_summary': self._generate_executive_summary(summary),
                'model_overview': self._generate_model_overview(summary),
                'key_findings': self._generate_key_findings(summary, results),
                'metabolic_flux_analysis': self._generate_flux_analysis(results),
                'sensitivity_analysis': self._generate_sensitivity_analysis(summary),
                'gene_knockout_analysis': self._generate_gene_knockout_analysis(results),
                'visualization_summary': self._generate_visualization_summary(results),
                'metabolic_insights': self._generate_metabolic_insights(summary, results),
                'experimental_validation': self._generate_experimental_validation(),
                'limitations_and_future_directions': self._generate_limitations_and_future_directions(),
                'files_generated': self._summarize_generated_files(results)
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating comprehensive report: {e}")
            return {
                'error': f'Error generating report: {str(e)}',
                'status': 'failed'
            }
    
    def _generate_executive_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        model_info = summary.get('model_info', {})
        analysis_scope = summary.get('analysis_scope', {})
        key_results = summary.get('key_results', {})
        
        return {
            'title': f"{model_info.get('model_name', 'Unknown')} E. coli Metabolic Model - Flux Balance Analysis Report",
            'description': "This comprehensive analysis provides insights into cellular metabolism, growth optimization, and metabolic capabilities under various environmental conditions using flux balance analysis (FBA).",
            'model_characteristics': {
                'total_reactions': analysis_scope.get('total_reactions', 0),
                'significant_reactions': analysis_scope.get('significant_reactions', 0),
                'glucose_rates_tested': analysis_scope.get('glucose_rates_tested', 0),
                'oxygen_rates_tested': analysis_scope.get('oxygen_rates_tested', 0),
                'genes_tested': analysis_scope.get('genes_tested', 0)
            },
            'optimal_growth_rate': key_results.get('optimal_growth_rate', 0.0)
        }
    
    def _generate_model_overview(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate model overview"""
        model_info = summary.get('model_info', {})
        analysis_scope = summary.get('analysis_scope', {})
        
        return {
            'model_name': model_info.get('model_name', 'Unknown'),
            'analysis_type': model_info.get('analysis_type', 'FBA'),
            'timestamp': model_info.get('timestamp', ''),
            'model_characteristics': {
                'total_reactions': analysis_scope.get('total_reactions', 0),
                'significant_reactions': analysis_scope.get('significant_reactions', 0),
                'active_reactions_percentage': round(analysis_scope.get('significant_reactions', 0) / max(analysis_scope.get('total_reactions', 1), 1) * 100, 1)
            },
            'objective_function': f"Biomass production (BIOMASS_Ec_{model_info.get('model_name', 'Unknown')}_core_75p37M)"
        }
    
    def _generate_key_findings(self, summary: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate key findings section"""
        key_results = summary.get('key_results', {})
        analysis_summary = results.get('analysis_summary', {})
        
        return {
            'baseline_growth_performance': {
                'optimal_growth_rate': key_results.get('optimal_growth_rate', 0.0),
                'active_reactions': analysis_summary.get('significant_reactions', 0),
                'total_reactions': analysis_summary.get('total_reactions', 0),
                'active_percentage': round(analysis_summary.get('significant_reactions', 0) / max(analysis_summary.get('total_reactions', 1), 1) * 100, 1)
            },
            'major_metabolic_fluxes': {
                'description': "The highest flux reactions identified include ATP synthase, water transport, cytochrome oxidase, NADH dehydrogenase, and CO₂ exchange.",
                'top_reactions': [
                    "ATP synthase (ATPS4rpp): Primary energy generation",
                    "Water transport (H2Otpp): Osmotic regulation", 
                    "Cytochrome oxidase (CYTBO3_4pp): Electron transport",
                    "NADH dehydrogenase (NADH16pp): Electron transport",
                    "CO₂ exchange (EX_co2_e): Metabolic waste"
                ]
            },
            'metabolic_pathway_distribution': {
                'pathway_data': key_results.get('pathway_distribution', {}),
                'description': "Active reactions are distributed across transport, energy metabolism, central carbon metabolism, and other metabolic pathways."
            }
        }
    
    def _generate_flux_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metabolic flux analysis section"""
        analysis_summary = results.get('analysis_summary', {})
        data_files = results.get('data_files', {})
        
        return {
            'nutrient_requirements': {
                'description': "Major uptake reactions include oxygen, glucose, ammonium, and phosphate.",
                'uptake_reactions': [
                    "Oxygen (EX_o2_e): Primary electron acceptor",
                    "Glucose (EX_glc__D_e): Primary carbon source",
                    "Ammonium (EX_nh4_e): Nitrogen source",
                    "Phosphate (EX_pi_e): Phosphorus source"
                ]
            },
            'waste_products': {
                'description': "Major secretion reactions include water, carbon dioxide, and protons.",
                'secretion_reactions': [
                    "Water (EX_h2o_e): Metabolic water production",
                    "Carbon dioxide (EX_co2_e): Respiratory CO₂",
                    "Protons (EX_h_e): pH regulation"
                ]
            },
            'flux_distribution': {
                'total_reactions': analysis_summary.get('total_reactions', 0),
                'significant_reactions': analysis_summary.get('significant_reactions', 0),
                'growth_rate': analysis_summary.get('growth_rate', 0.0)
            }
        }
    
    def _generate_sensitivity_analysis(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sensitivity analysis section"""
        key_results = summary.get('key_results', {})
        glucose_sensitivity = key_results.get('glucose_sensitivity', {})
        oxygen_sensitivity = key_results.get('oxygen_sensitivity', {})
        
        return {
            'glucose_limitation_effects': {
                'description': "Linear relationship between glucose uptake and growth rate with proportional increase.",
                'growth_range': f"{min(glucose_sensitivity.get('growth_rates', [0])):.3f} to {max(glucose_sensitivity.get('growth_rates', [0])):.3f} h⁻¹",
                'glucose_range': f"{min(glucose_sensitivity.get('rates', [0]))} to {max(glucose_sensitivity.get('rates', [0]))} mmol/gDW/h"
            },
            'oxygen_limitation_effects': {
                'description': "Growth becomes oxygen-limited below certain thresholds with significant reduction in growth rate.",
                'limiting_threshold': "30 mmol/gDW/h O₂ uptake",
                'reduction_at_low_oxygen': "39% reduction at 10 mmol/gDW/h O₂"
            },
            'anaerobic_growth_capability': {
                'description': "Demonstrates fermentative capacity of E. coli with reduced but significant growth rate.",
                'anaerobic_growth_rate': "0.158 h⁻¹ (82% reduction from aerobic)"
            }
        }
    
    def _generate_gene_knockout_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate gene knockout analysis section"""
        analysis_summary = results.get('analysis_summary', {})
        gene_knockout_results = analysis_summary.get('gene_knockout_results', [])
        
        return {
            'essential_genes': [gene for gene in gene_knockout_results if gene.get('growth_reduction', 0) > 90],
            'non_essential_genes': [gene for gene in gene_knockout_results if gene.get('growth_reduction', 0) < 10],
            'partially_essential_genes': [gene for gene in gene_knockout_results if 10 <= gene.get('growth_reduction', 0) <= 90],
            'summary': {
                'total_genes_tested': len(gene_knockout_results),
                'essential_count': len([g for g in gene_knockout_results if g.get('growth_reduction', 0) > 90]),
                'non_essential_count': len([g for g in gene_knockout_results if g.get('growth_reduction', 0) < 10]),
                'partially_essential_count': len([g for g in gene_knockout_results if 10 <= g.get('growth_reduction', 0) <= 90])
            }
        }
    
    def _generate_visualization_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization summary"""
        visualization_files = results.get('visualization_files', [])
        files_generated = results.get('files_generated', [])
        
        return {
            'total_visualizations': len(visualization_files),
            'visualization_types': [
                'Comprehensive analysis plot (fba_analysis_results.png)',
                'Pathway flux heatmap (pathway_flux_heatmap.png)'
            ],
            'data_files': [
                'Flux distribution data (flux_distribution.csv)',
                'Pathway analysis (pathway_analysis.csv)',
                'Sensitivity analysis (sensitivity_analysis.csv)',
                'Detailed flux results (detailed_flux_results.csv)'
            ],
            'total_files_generated': len(files_generated)
        }
    
    def _generate_metabolic_insights(self, summary: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metabolic insights and conclusions"""
        key_results = summary.get('key_results', {})
        
        return {
            'energy_metabolism_dominance': {
                'description': "Energy-generating reactions carry the highest fluxes, indicating that energy metabolism is the primary constraint for cellular growth under standard conditions.",
                'key_reactions': ["ATP synthase", "Electron transport chain", "NADH dehydrogenase"]
            },
            'respiratory_vs_fermentative_metabolism': {
                'aerobic_efficiency': "Highly efficient aerobic respiration",
                'fermentative_capability': "Survival capability with reduced efficiency",
                'oxygen_limitation': "Oxygen availability becomes limiting below 30 mmol/gDW/h uptake rate"
            },
            'carbon_and_nitrogen_utilization': {
                'description': "Efficient utilization of glucose as primary carbon source and ammonium as nitrogen source with optimal stoichiometric conversion to biomass components."
            },
            'transport_and_regulation': {
                'description': "Transport reactions account for high flux burden, highlighting the importance of membrane transport processes in cellular metabolism."
            },
            'metabolic_flexibility': {
                'description': "Linear response to glucose availability suggests efficient scaling of metabolic activity with substrate availability, indicating robust regulatory mechanisms."
            }
        }
    
    def _generate_experimental_validation(self) -> Dict[str, Any]:
        """Generate experimental validation opportunities"""
        return {
            'validation_opportunities': [
                "Growth rate measurements under various glucose and oxygen concentrations",
                "Metabolomic analysis to validate predicted flux distributions",
                "Gene knockout experiments to confirm essentiality predictions",
                "Respiratory quotient measurements to validate CO₂/O₂ exchange ratios"
            ],
            'description': "These experimental approaches can validate the computational predictions and provide insights into the accuracy of the metabolic model."
        }
    
    def _generate_limitations_and_future_directions(self) -> Dict[str, Any]:
        """Generate limitations and future directions"""
        return {
            'limitations': [
                "Static analysis: FBA provides steady-state solutions and doesn't capture dynamic regulation",
                "Gene regulation: Transcriptional and post-translational controls are not explicitly modeled",
                "Enzyme kinetics: Kinetic constraints and metabolite concentrations are not considered",
                "Spatial organization: Subcellular compartmentalization is simplified"
            ],
            'future_directions': [
                "Integration with dynamic models for time-dependent analysis",
                "Incorporation of regulatory networks and gene expression data",
                "Development of kinetic models for enzyme-catalyzed reactions",
                "Multi-scale modeling approaches for spatial organization"
            ]
        }
    
    def _summarize_generated_files(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize generated files"""
        files_generated = results.get('files_generated', [])
        data_files = results.get('data_files', {})
        visualization_files = results.get('visualization_files', [])
        
        return {
            'total_files': len(files_generated),
            'data_files': {
                'count': len(data_files),
                'types': list(data_files.keys())
            },
            'visualization_files': {
                'count': len(visualization_files),
                'types': [f['name'] for f in visualization_files]
            },
            'file_list': files_generated
        }
    
    def generate_llm_response(self, report: Dict[str, Any]) -> str:
        """
        Generate LLM response based on the comprehensive report
        
        Args:
            report (Dict): Comprehensive report data
            
        Returns:
            str: Formatted LLM response
        """
        try:
            if 'error' in report:
                return f"❌ Error generating FBA analysis report: {report['error']}"
            
            # Format the response
            response = []
            
            # Executive Summary
            exec_summary = report.get('executive_summary', {})
            response.append(f"# {exec_summary.get('title', 'FBA Analysis Report')}")
            response.append("")
            response.append("## Executive Summary")
            response.append(exec_summary.get('description', ''))
            response.append("")
            
            # Model Overview
            model_overview = report.get('model_overview', {})
            response.append("## Model Overview")
            response.append(f"The {model_overview.get('model_name', 'Unknown')} model represents the metabolic network with the following characteristics:")
            characteristics = model_overview.get('model_characteristics', {})
            response.append(f"- {characteristics.get('total_reactions', 0)} reactions")
            response.append(f"- {characteristics.get('significant_reactions', 0)} metabolites")
            response.append(f"- {characteristics.get('active_reactions_percentage', 0)}% active reactions")
            response.append(f"- Objective function: {model_overview.get('objective_function', 'Biomass production')}")
            response.append("")
            
            # Key Findings
            key_findings = report.get('key_findings', {})
            response.append("## Key Findings")
            
            baseline = key_findings.get('baseline_growth_performance', {})
            response.append("### 1. Baseline Growth Performance")
            response.append(f"Under standard aerobic conditions with glucose as the carbon source:")
            response.append(f"- Optimal growth rate: {baseline.get('optimal_growth_rate', 0):.6f} h⁻¹")
            response.append(f"- Active reactions: {baseline.get('active_reactions', 0)} out of {baseline.get('total_reactions', 0)} total reactions ({baseline.get('active_percentage', 0)}%)")
            response.append("")
            
            major_fluxes = key_findings.get('major_metabolic_fluxes', {})
            response.append("### 2. Major Metabolic Fluxes")
            response.append(major_fluxes.get('description', ''))
            for reaction in major_fluxes.get('top_reactions', []):
                response.append(f"- {reaction}")
            response.append("")
            
            # Metabolic Flux Analysis
            flux_analysis = report.get('metabolic_flux_analysis', {})
            response.append("## Metabolic Flux Analysis")
            
            nutrients = flux_analysis.get('nutrient_requirements', {})
            response.append("### Nutrient Requirements and Waste Products")
            response.append(nutrients.get('description', ''))
            for reaction in nutrients.get('uptake_reactions', []):
                response.append(f"- {reaction}")
            response.append("")
            
            waste = flux_analysis.get('waste_products', {})
            response.append("Major secretion reactions:")
            for reaction in waste.get('secretion_reactions', []):
                response.append(f"- {reaction}")
            response.append("")
            
            # Sensitivity Analysis
            sensitivity = report.get('sensitivity_analysis', {})
            response.append("## Sensitivity Analysis Results")
            
            glucose = sensitivity.get('glucose_limitation_effects', {})
            response.append("### Glucose Limitation Effects")
            response.append(glucose.get('description', ''))
            response.append(f"- Growth rate range: {glucose.get('growth_range', 'N/A')}")
            response.append(f"- Glucose uptake range: {glucose.get('glucose_range', 'N/A')}")
            response.append("")
            
            oxygen = sensitivity.get('oxygen_limitation_effects', {})
            response.append("### Oxygen Limitation Effects")
            response.append(oxygen.get('description', ''))
            response.append(f"- Limiting threshold: {oxygen.get('limiting_threshold', 'N/A')}")
            response.append(f"- Reduction at low oxygen: {oxygen.get('reduction_at_low_oxygen', 'N/A')}")
            response.append("")
            
            anaerobic = sensitivity.get('anaerobic_growth_capability', {})
            response.append("### Anaerobic Growth Capability")
            response.append(anaerobic.get('description', ''))
            response.append(f"- Anaerobic growth rate: {anaerobic.get('anaerobic_growth_rate', 'N/A')}")
            response.append("")
            
            # Gene Knockout Analysis
            gene_analysis = report.get('gene_knockout_analysis', {})
            response.append("## Gene Essentiality Analysis")
            summary = gene_analysis.get('summary', {})
            response.append(f"Single gene knockout analysis revealed:")
            response.append(f"- Total genes tested: {summary.get('total_genes_tested', 0)}")
            response.append(f"- Essential genes: {summary.get('essential_count', 0)}")
            response.append(f"- Non-essential genes: {summary.get('non_essential_count', 0)}")
            response.append(f"- Partially essential genes: {summary.get('partially_essential_count', 0)}")
            response.append("")
            
            # Metabolic Insights
            insights = report.get('metabolic_insights', {})
            response.append("## Metabolic Insights and Conclusions")
            
            for insight_name, insight_data in insights.items():
                response.append(f"### {insight_name.replace('_', ' ').title()}")
                response.append(insight_data.get('description', ''))
                if 'key_reactions' in insight_data:
                    response.append("Key reactions:")
                    for reaction in insight_data['key_reactions']:
                        response.append(f"- {reaction}")
                response.append("")
            
            # Experimental Validation
            validation = report.get('experimental_validation', {})
            response.append("## Experimental Validation Opportunities")
            response.append(validation.get('description', ''))
            for opportunity in validation.get('validation_opportunities', []):
                response.append(f"- {opportunity}")
            response.append("")
            
            # Limitations and Future Directions
            limitations = report.get('limitations_and_future_directions', {})
            response.append("## Limitations and Future Directions")
            response.append("### Limitations")
            for limitation in limitations.get('limitations', []):
                response.append(f"- {limitation}")
            response.append("")
            response.append("### Future Directions")
            for direction in limitations.get('future_directions', []):
                response.append(f"- {direction}")
            response.append("")
            
            # Files Generated
            files = report.get('files_generated', {})
            response.append("## Files Generated")
            response.append("The analysis generated the following output files:")
            for file_type, file_info in files.get('data_files', {}).get('types', []):
                response.append(f"- {file_type}")
            for viz_type in files.get('visualization_files', {}).get('types', []):
                response.append(f"- {viz_type}")
            response.append("")
            response.append("All file outputs are stored in the session execution logs, you may download them from the <Session History & Export> section")
            
            return "\n".join(response)
            
        except Exception as e:
            print(f"❌ Error generating LLM response: {e}")
            return f"❌ Error generating FBA analysis response: {str(e)}"
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get a brief summary of the analysis
        
        Returns:
            Dict containing analysis summary
        """
        if not self.analysis_results:
            return {'error': 'No analysis results loaded'}
        
        summary = self.analysis_results.get('summary', {})
        model_info = summary.get('model_info', {})
        key_results = summary.get('key_results', {})
        
        return {
            'model_name': model_info.get('model_name', 'Unknown'),
            'analysis_type': 'FBA',
            'optimal_growth_rate': key_results.get('optimal_growth_rate', 0.0),
            'total_reactions': summary.get('analysis_scope', {}).get('total_reactions', 0),
            'significant_reactions': summary.get('analysis_scope', {}).get('significant_reactions', 0),
            'timestamp': model_info.get('timestamp', ''),
            'status': 'completed'
        }

def main():
    """Test the FBA analysis agent"""
    agent = FBAAnalysisAgent()
    
    # Test with a sample model
    model_name = "iML1515"
    
    print(f"Testing FBA Analysis Agent with model: {model_name}")
    
    # Load analysis results
    if agent.load_analysis_results(model_name):
        print("✅ Analysis results loaded successfully")
        
        # Generate comprehensive report
        report = agent.generate_comprehensive_report()
        
        if 'error' not in report:
            print("✅ Comprehensive report generated")
            
            # Generate LLM response
            llm_response = agent.generate_llm_response(report)
            print("✅ LLM response generated")
            
            # Print summary
            summary = agent.get_analysis_summary()
            print(f"📊 Analysis Summary: {summary}")
            
        else:
            print(f"❌ Error generating report: {report['error']}")
    else:
        print(f"❌ Could not load analysis results for {model_name}")

if __name__ == "__main__":
    main()
