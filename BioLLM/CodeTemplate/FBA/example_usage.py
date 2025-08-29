"""
Example Usage of FBA Templates
This file demonstrates how to use the FBA analysis templates with different configurations.
"""

import os
import sys
import subprocess
import tempfile
import shutil

def create_custom_fba_script(model_url, model_name, output_dir, glucose_rates, oxygen_rates, test_genes):
    """
    Create a custom FBA script by replacing slots in the template
    
    Args:
        model_url (str): URL to download the metabolic model
        model_name (str): Name of the model
        output_dir (str): Output directory for results
        glucose_rates (list): List of glucose uptake rates to test
        oxygen_rates (list): List of oxygen availability rates to test
        test_genes (list): List of genes to test in knockout analysis
    """
    
    # Read the simple template
    template_path = "simple_fba_template.py"
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace slots with actual values
    custom_content = template_content.replace('{{MODEL_URL}}', model_url)
    custom_content = custom_content.replace('{{MODEL_NAME}}', model_name)
    custom_content = custom_content.replace('{{BIOMASS_REACTION_ID}}', f'BIOMASS_Ec_{model_name}_core_75p37M')
    custom_content = custom_content.replace('{{OUTPUT_DIR}}', output_dir)
    custom_content = custom_content.replace('{{GLUCOSE_RATES}}', str(glucose_rates))
    custom_content = custom_content.replace('{{OXYGEN_RATES}}', str(oxygen_rates))
    custom_content = custom_content.replace('{{FLUX_THRESHOLD}}', '0.001')
    custom_content = custom_content.replace('{{TEST_GENES}}', str(test_genes))
    custom_content = custom_content.replace('{{KEY_REACTIONS}}', str([
        f'BIOMASS_Ec_{model_name}_core_75p37M',
        'EX_glc__D_e',
        'EX_o2_e',
        'EX_co2_e',
        'EX_h2o_e',
        'ATPS4rpp',
        'CYTBO3_4pp'
    ]))
    
    # Write the custom script
    custom_script_path = f"custom_fba_{model_name}.py"
    with open(custom_script_path, 'w') as f:
        f.write(custom_content)
    
    print(f"Custom FBA script created: {custom_script_path}")
    return custom_script_path

def run_fba_analysis(script_path):
    """
    Run the FBA analysis script
    
    Args:
        script_path (str): Path to the FBA script to run
    """
    try:
        print(f"Running FBA analysis: {script_path}")
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("FBA analysis completed successfully!")
            print("Output:")
            print(result.stdout)
        else:
            print("FBA analysis failed!")
            print("Error:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("FBA analysis timed out after 5 minutes")
    except Exception as e:
        print(f"Error running FBA analysis: {e}")

def example_1_basic_usage():
    """Example 1: Basic usage with iML1515 model"""
    print("=" * 60)
    print("Example 1: Basic FBA Analysis with iML1515")
    print("=" * 60)
    
    # Configuration
    model_url = "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"
    model_name = "iML1515"
    output_dir = "/tmp/fba_example_1"
    glucose_rates = [5, 10, 15, 20, 25]
    oxygen_rates = [10, 20, 30, 40, 50]
    test_genes = ['b0008', 'b0114', 'b1136']
    
    # Create custom script
    script_path = create_custom_fba_script(
        model_url, model_name, output_dir, 
        glucose_rates, oxygen_rates, test_genes
    )
    
    # Run analysis
    run_fba_analysis(script_path)
    
    # Clean up
    os.remove(script_path)
    print(f"Cleaned up: {script_path}")

def example_2_different_model():
    """Example 2: Using a different model (iJO1366)"""
    print("\n" + "=" * 60)
    print("Example 2: FBA Analysis with iJO1366 Model")
    print("=" * 60)
    
    # Configuration for iJO1366
    model_url = "http://bigg.ucsd.edu/static/models/iJO1366.xml.gz"
    model_name = "iJO1366"
    output_dir = "/tmp/fba_example_2"
    glucose_rates = [1, 2, 5, 10, 15]  # Different range for iJO1366
    oxygen_rates = [5, 10, 15, 20, 25]  # Different range
    test_genes = ['b0008', 'b0114', 'b1136', 'b2925']  # More genes
    
    # Create custom script
    script_path = create_custom_fba_script(
        model_url, model_name, output_dir, 
        glucose_rates, oxygen_rates, test_genes
    )
    
    # Run analysis
    run_fba_analysis(script_path)
    
    # Clean up
    os.remove(script_path)
    print(f"Cleaned up: {script_path}")

def example_3_custom_parameters():
    """Example 3: Custom analysis parameters"""
    print("\n" + "=" * 60)
    print("Example 3: Custom FBA Analysis Parameters")
    print("=" * 60)
    
    # Custom configuration
    model_url = "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"
    model_name = "iML1515_custom"
    output_dir = "/tmp/fba_example_3"
    glucose_rates = [0.1, 0.5, 1.0, 2.0, 5.0]  # Very low glucose rates
    oxygen_rates = [1, 2, 5, 10, 15]  # Low oxygen rates
    test_genes = ['b0008', 'b0114', 'b1136', 'b2925', 'b0720', 'b0721']  # Extended gene list
    
    # Create custom script
    script_path = create_custom_fba_script(
        model_url, model_name, output_dir, 
        glucose_rates, oxygen_rates, test_genes
    )
    
    # Run analysis
    run_fba_analysis(script_path)
    
    # Clean up
    os.remove(script_path)
    print(f"Cleaned up: {script_path}")

def example_4_agent_system_integration():
    """Example 4: How agent system would integrate with templates"""
    print("\n" + "=" * 60)
    print("Example 4: Agent System Integration")
    print("=" * 60)
    
    # Simulate agent system providing parameters
    agent_parameters = {
        'model_url': "http://bigg.ucsd.edu/static/models/iML1515.xml.gz",
        'model_name': "iML1515_agent",
        'output_dir': "/tmp/agent_fba_analysis",
        'glucose_rates': [2, 4, 6, 8, 10],
        'oxygen_rates': [8, 12, 16, 20, 24],
        'test_genes': ['b0008', 'b0114'],
        'flux_threshold': 0.0005  # Lower threshold for more sensitive analysis
    }
    
    print("Agent system would provide these parameters:")
    for key, value in agent_parameters.items():
        print(f"  {key}: {value}")
    
    # Create custom script with agent parameters
    script_path = create_custom_fba_script(
        agent_parameters['model_url'],
        agent_parameters['model_name'],
        agent_parameters['output_dir'],
        agent_parameters['glucose_rates'],
        agent_parameters['oxygen_rates'],
        agent_parameters['test_genes']
    )
    
    # Run analysis
    run_fba_analysis(script_path)
    
    # Clean up
    os.remove(script_path)
    print(f"Cleaned up: {script_path}")

def main():
    """Run all examples"""
    print("FBA Template Usage Examples")
    print("This script demonstrates how to use the FBA analysis templates.")
    print("Note: These examples require internet connection to download models.")
    print()
    
    try:
        # Run examples
        example_1_basic_usage()
        example_2_different_model()
        example_3_custom_parameters()
        example_4_agent_system_integration()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("Check the output directories for results:")
        print("  /tmp/fba_example_1")
        print("  /tmp/fba_example_2")
        print("  /tmp/fba_example_3")
        print("  /tmp/agent_fba_analysis")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
