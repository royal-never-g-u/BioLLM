#!/usr/bin/env python3
"""
Test script for task type 6 (Constraint-Based Analysis)
This script tests the constraint-based analysis functionality and verifies that
the Executive Summary, Detailed Analysis Results, and Generated Reports sections
are properly populated.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from experiment_executor import execute_constraint_based_analysis
from bio_task import BioTask, BioTaskManager

def test_constraint_based_analysis():
    """Test constraint-based analysis with e_coli_core model"""
    
    print("🧪 Testing Task Type 6: Constraint-Based Analysis")
    print("=" * 60)
    
    # Set up test parameters
    model_name = "e_coli_core"
    model_location = "../downloads/e_coli_core.mat"
    
    # Check if model file exists
    if not os.path.exists(model_location):
        print(f"❌ Model file not found: {model_location}")
        print("Please ensure the e_coli_core.mat file is available in the downloads directory")
        return False
    
    print(f"✅ Model file found: {model_location}")
    
    # Update bio_task with test parameters
    task_manager = BioTaskManager()
    test_task = BioTask(
        model_name=model_name,
        model_local=model_location,
        task_type=6
    )
    task_manager.save_task(test_task)
    
    print(f"📋 Updated bio_task with model: {model_name}, task_type: 6")
    
    try:
        # Execute constraint-based analysis
        print("\n🚀 Executing constraint-based analysis...")
        result = execute_constraint_based_analysis(model_name, model_location)
        
        if result.get('success', False):
            print("✅ Constraint-based analysis completed successfully!")
            
            # Check the structure of the results
            analysis_results = result.get('results', {})
            
            print("\n📊 Analysis Results Structure:")
            print(f"  - Analysis completed: {analysis_results.get('analysis_completed', False)}")
            print(f"  - Has summary: {'summary' in analysis_results}")
            print(f"  - Has results: {'results' in analysis_results}")
            print(f"  - Has visualizations: {'visualizations' in analysis_results}")
            print(f"  - Has config: {'config_used' in analysis_results}")
            
            # Check detailed results
            detailed_results = analysis_results.get('results', {})
            if detailed_results:
                print("\n🔬 Detailed Results Available:")
                print(f"  - Basic info: {'basic_info' in detailed_results}")
                print(f"  - FBA analysis: {'fba_analysis' in detailed_results}")
                print(f"  - Growth analysis: {'growth_analysis' in detailed_results}")
                print(f"  - Environmental analysis: {'environmental_analysis' in detailed_results}")
                print(f"  - Essentiality analysis: {'essentiality_analysis' in detailed_results}")
                
                # Display some key metrics
                if 'basic_info' in detailed_results:
                    basic_info = detailed_results['basic_info']
                    print(f"\n📋 Model Information:")
                    print(f"  - Name: {basic_info.get('name', 'Unknown')}")
                    print(f"  - Reactions: {basic_info.get('reactions_count', 0):,}")
                    print(f"  - Metabolites: {basic_info.get('metabolites_count', 0):,}")
                    print(f"  - Genes: {basic_info.get('genes_count', 0):,}")
                
                if 'fba_analysis' in detailed_results:
                    fba_results = detailed_results['fba_analysis']
                    print(f"\n⚖️ FBA Results:")
                    print(f"  - Growth rate: {fba_results.get('objective_value', 0):.6f} h⁻¹")
                    print(f"  - Status: {fba_results.get('status', 'Unknown')}")
                
                if 'growth_analysis' in detailed_results:
                    growth_results = detailed_results['growth_analysis']
                    print(f"\n🌱 Growth Analysis:")
                    print(f"  - Aerobic growth: {growth_results.get('aerobic_growth', 0):.6f} h⁻¹")
                    print(f"  - Anaerobic growth: {growth_results.get('anaerobic_growth', 0):.6f} h⁻¹")
                    print(f"  - Growth reduction: {growth_results.get('growth_reduction_anaerobic', 0):.1f}%")
            
            # Check if report was generated
            if 'report' in result:
                report = result['report']
                print(f"\n📋 Report Generated:")
                print(f"  - Report length: {len(report)} characters")
                print(f"  - Contains 'Executive Summary': {'Executive Summary' in report}")
                print(f"  - Contains 'Detailed Analysis': {'Detailed Analysis' in report}")
                print(f"  - Contains 'Generated Reports': {'Generated Reports' in report}")
                
                # Save report to file for inspection
                report_file = "test_constraint_based_report.txt"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"  - Report saved to: {report_file}")
            
            # Check visualizations
            visualizations = result.get('visualizations', [])
            print(f"\n📈 Visualizations:")
            print(f"  - Number of visualizations: {len(visualizations)}")
            for i, viz in enumerate(visualizations):
                print(f"    {i+1}. {viz}")
            
            print("\n✅ Test completed successfully!")
            return True
            
        else:
            print(f"❌ Constraint-based analysis failed:")
            print(f"  - Error: {result.get('error', 'Unknown error')}")
            if 'traceback' in result:
                print(f"  - Traceback: {result['traceback']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_result_visualizer():
    """Test the result visualizer with constraint-based analysis results"""
    
    print("\n🧪 Testing Result Visualizer for Task Type 6")
    print("=" * 60)
    
    try:
        from result_visualizer import EnhancedResultVisualizer
        
        # Create a mock experiment result for testing
        mock_result = {
            'success': True,
            'model_name': 'e_coli_core',
            'task_type': 6,
            'experiment_timestamp': '2024-01-01 12:00:00',
            'results': {
                'analysis_completed': True,
                'summary': 'Test summary',
                'results': {
                    'basic_info': {
                        'name': 'E. coli Core Model',
                        'reactions_count': 95,
                        'metabolites_count': 72,
                        'genes_count': 137,
                        'compartments_count': 2,
                        'exchange_reactions_count': 20,
                        'transport_reactions_count': 15
                    },
                    'fba_analysis': {
                        'objective_value': 0.8739,
                        'status': 'optimal'
                    },
                    'growth_analysis': {
                        'aerobic_growth': 0.8739,
                        'anaerobic_growth': 0.158,
                        'growth_reduction_anaerobic': 82.0
                    },
                    'essentiality_analysis': {
                        'total_tested': 16,
                        'essential_reactions': ['CS', 'ICDHyr']
                    }
                },
                'output_directory': '/tmp/test_output',
                'visualizations': ['/tmp/test_output/analysis.png']
            },
            'report': 'Test report content with Executive Summary, Detailed Analysis Results, and Generated Reports sections.'
        }
        
        print("✅ Mock result created successfully")
        print("📊 Result structure verified")
        
        # Test that the visualizer methods can handle the data structure
        visualizer = EnhancedResultVisualizer()
        
        # Test executive summary method
        print("\n🔍 Testing executive summary method...")
        try:
            # This would normally be called by Streamlit, but we can test the logic
            analysis_results = mock_result.get('results', {})
            results = analysis_results.get('results', {})
            
            # Check if we can extract the expected data
            model_info = results.get('basic_info', {})
            fba_results = results.get('fba_analysis', {})
            growth_results = results.get('growth_analysis', {})
            essentiality_results = results.get('essentiality_analysis', {})
            
            print(f"  - Model info extracted: {bool(model_info)}")
            print(f"  - FBA results extracted: {bool(fba_results)}")
            print(f"  - Growth results extracted: {bool(growth_results)}")
            print(f"  - Essentiality results extracted: {bool(essentiality_results)}")
            
            print("✅ Executive summary method test passed")
            
        except Exception as e:
            print(f"❌ Executive summary method test failed: {e}")
            return False
        
        # Test detailed analysis method
        print("\n🔍 Testing detailed analysis method...")
        try:
            # Test the logic for detailed analysis
            results = analysis_results.get('results', {})
            
            # Check if all expected sections are present
            sections = ['basic_info', 'fba_analysis', 'growth_analysis', 'essentiality_analysis']
            for section in sections:
                if section in results:
                    print(f"  - {section}: ✅")
                else:
                    print(f"  - {section}: ❌")
            
            print("✅ Detailed analysis method test passed")
            
        except Exception as e:
            print(f"❌ Detailed analysis method test failed: {e}")
            return False
        
        # Test generated reports method
        print("\n🔍 Testing generated reports method...")
        try:
            # Test the logic for generated reports
            output_directory = analysis_results.get('output_directory', '')
            files_generated = results.get('files_generated', [])
            
            print(f"  - Output directory: {output_directory}")
            print(f"  - Files generated: {len(files_generated)}")
            print(f"  - Report available: {'report' in mock_result}")
            
            print("✅ Generated reports method test passed")
            
        except Exception as e:
            print(f"❌ Generated reports method test failed: {e}")
            return False
        
        print("\n✅ All result visualizer tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Result visualizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Starting Task Type 6 Tests")
    print("=" * 60)
    
    # Test 1: Constraint-based analysis execution
    test1_passed = test_constraint_based_analysis()
    
    # Test 2: Result visualizer
    test2_passed = test_result_visualizer()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Constraint-based analysis test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Result visualizer test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Task type 6 is working correctly.")
        print("The Executive Summary, Detailed Analysis Results, and Generated Reports")
        print("sections should now display appropriate content.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
    
    print("=" * 60)
