#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Streamlit Figures Structure

This script helps debug the structure of streamlit figures to understand
why cobra visual figures are not being displayed.
"""

import os
import sys
from agent.model_analyzer_agent import ModelAnalyzerAgent

def debug_streamlit_figures():
    """Debug streamlit figures structure"""
    
    print("="*60)
    print("Debugging Streamlit Figures Structure")
    print("="*60)
    
    # Initialize agent
    agent = ModelAnalyzerAgent()
    
    # Run analyse command
    result = agent.run("analyse e_coli_core")
    
    print(f"✅ Analyse command completed")
    print(f"📊 Result length: {len(result)} characters")
    
    # Check streamlit figures
    if hasattr(agent, 'streamlit_figures') and agent.streamlit_figures:
        print(f"\n✅ Streamlit figures generated: {len(agent.streamlit_figures)}")
        
        # Analyze each figure
        for i, figure in enumerate(agent.streamlit_figures):
            print(f"\n--- Figure {i+1} ---")
            print(f"Type: {type(figure)}")
            
            if isinstance(figure, dict):
                print("Dictionary structure:")
                for key, value in figure.items():
                    print(f"  {key}: {value}")
                
                # Check if this is a cobra visual figure
                name = figure.get('name', '')
                title = figure.get('title', '')
                if 'Cobra Visual' in name or 'Cobra Visual' in title:
                    print("🎨 This appears to be a cobra visual figure!")
                else:
                    print("🔬 This appears to be a regular analysis figure")
                    
            elif isinstance(figure, tuple):
                print(f"Tuple structure: {len(figure)} elements")
                for j, item in enumerate(figure):
                    print(f"  Element {j}: {type(item)} = {item}")
            else:
                print(f"Other structure: {figure}")
    
    else:
        print("❌ No streamlit figures generated")
    
    # Check cobra visual directory
    cobra_visual_dir = "model_data/e_coli_core/cobra_visual"
    if os.path.exists(cobra_visual_dir):
        print(f"\n✅ Cobra visual directory exists: {cobra_visual_dir}")
        files = os.listdir(cobra_visual_dir)
        print(f"📁 Files in cobra_visual directory: {len(files)}")
        for file in sorted(files):
            print(f"  📄 {file}")
    else:
        print(f"\n❌ Cobra visual directory does not exist: {cobra_visual_dir}")

def main():
    """Main function"""
    debug_streamlit_figures()

if __name__ == "__main__":
    main()
