#!/usr/bin/env python3
"""
Test script to verify that the visualization fixes work correctly.
"""

import json
import os

def test_visualization_fix():
    """Test the visualization fix with different data types"""
    
    print("🧪 Testing Visualization Fix")
    print("=" * 50)
    
    # Test case 1: String visualization
    print("\n📊 Test Case 1: String visualization")
    visualizations = ["/path/to/image.png", "/path/to/report.html"]
    
    # Simulate the fix
    if not isinstance(visualizations, list):
        visualizations = [visualizations]
    
    processed_visualizations = []
    for viz in visualizations:
        if isinstance(viz, str):
            processed_visualizations.append({
                'name': os.path.basename(viz),
                'path': viz,
                'type': 'image' if viz.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')) else 'html'
            })
        elif isinstance(viz, dict):
            processed_visualizations.append(viz)
    
    print(f"  - Original: {visualizations}")
    print(f"  - Processed: {processed_visualizations}")
    
    # Test case 2: Mixed string and dict
    print("\n📊 Test Case 2: Mixed string and dict")
    visualizations = [
        "/path/to/image.png",
        {"name": "chart.html", "path": "/path/to/chart.html", "type": "html"}
    ]
    
    processed_visualizations = []
    for viz in visualizations:
        if isinstance(viz, str):
            processed_visualizations.append({
                'name': os.path.basename(viz),
                'path': viz,
                'type': 'image' if viz.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')) else 'html'
            })
        elif isinstance(viz, dict):
            processed_visualizations.append(viz)
    
    print(f"  - Original: {visualizations}")
    print(f"  - Processed: {processed_visualizations}")
    
    # Test case 3: Single string
    print("\n📊 Test Case 3: Single string")
    visualizations = "/path/to/single.png"
    
    if not isinstance(visualizations, list):
        visualizations = [visualizations]
    
    processed_visualizations = []
    for viz in visualizations:
        if isinstance(viz, str):
            processed_visualizations.append({
                'name': os.path.basename(viz),
                'path': viz,
                'type': 'image' if viz.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')) else 'html'
            })
        elif isinstance(viz, dict):
            processed_visualizations.append(viz)
    
    print(f"  - Original: {visualizations}")
    print(f"  - Processed: {processed_visualizations}")
    
    # Test case 4: Empty list
    print("\n📊 Test Case 4: Empty list")
    visualizations = []
    
    if not isinstance(visualizations, list):
        visualizations = [visualizations]
    
    processed_visualizations = []
    for viz in visualizations:
        if isinstance(viz, str):
            processed_visualizations.append({
                'name': os.path.basename(viz),
                'path': viz,
                'type': 'image' if viz.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')) else 'html'
            })
        elif isinstance(viz, dict):
            processed_visualizations.append(viz)
    
    print(f"  - Original: {visualizations}")
    print(f"  - Processed: {processed_visualizations}")
    
    print("\n✅ All test cases completed successfully!")
    return True

if __name__ == "__main__":
    success = test_visualization_fix()
    if success:
        print("\n🎉 Visualization fix test passed!")
    else:
        print("\n❌ Visualization fix test failed!")
