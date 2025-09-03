#!/usr/bin/env python3
"""
Demo script for LiteratureAgent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.literature_agent import LiteratureAgent

def demo_literature_agent():
    """Demonstrate the literature agent functionality"""
    print("=" * 80)
    print("Literature Agent Demo")
    print("=" * 80)
    print()
    
    # Initialize the agent
    print("Initializing Literature Agent...")
    agent = LiteratureAgent()
    print("✓ Literature Agent initialized successfully!")
    print()
    
    # Demo examples
    examples = [
        {
            "title": "代谢网络分析",
            "input": "I want to analyze metabolic networks using FBA",
            "description": "用户想要使用FBA分析代谢网络"
        },
        {
            "title": "基因删除分析",
            "input": "How to perform gene deletion analysis in E. coli",
            "description": "用户想要了解如何在E. coli中进行基因删除分析"
        },
        {
            "title": "酵母代谢约束分析",
            "input": "Constraint-based analysis of yeast metabolism",
            "description": "用户想要进行酵母代谢的约束基础分析"
        }
    ]
    
    print("Available demo examples:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']} - {example['description']}")
    print()
    
    # Get user choice
    while True:
        try:
            choice = input("Please select an example (1-3) or enter 'q' to quit: ").strip()
            if choice.lower() == 'q':
                print("Goodbye!")
                break
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(examples):
                selected_example = examples[choice_num - 1]
                break
            else:
                print("Invalid choice. Please select 1-3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    if choice.lower() == 'q':
        return
    
    # Run the selected example
    print(f"\n{'='*60}")
    print(f"Running: {selected_example['title']}")
    print(f"Input: {selected_example['input']}")
    print(f"{'='*60}")
    print()
    
    # Step 1: Extract keywords
    print("Step 1: Extracting keywords...")
    keywords = agent.extract_keywords(selected_example['input'])
    print(f"✓ Extracted keywords: {keywords}")
    print()
    
    # Step 2: Search for papers
    print("Step 2: Searching for papers...")
    paper_urls = agent.search_papers(keywords, max_results=3)
    print(f"✓ Found {len(paper_urls)} potential papers:")
    for i, url in enumerate(paper_urls, 1):
        print(f"  {i}. {url}")
    print()
    
    # Step 3: Ask user if they want to download
    download_choice = input("Do you want to download these papers? (y/n): ").strip().lower()
    
    if download_choice == 'y':
        print("\nStep 3: Downloading papers...")
        downloaded_papers = []
        failed_downloads = []
        
        for i, url in enumerate(paper_urls, 1):
            print(f"Downloading paper {i}/{len(paper_urls)}...")
            result = agent.download_paper(url, f"demo_paper_{choice_num}_{i}")
            
            if result['success']:
                downloaded_papers.append(result)
                print(f"✓ Downloaded: {result['filename']}")
            else:
                failed_downloads.append(url)
                print(f"✗ Failed: {result['message']}")
        
        print(f"\nDownload Summary:")
        print(f"- Successfully downloaded: {len(downloaded_papers)}")
        print(f"- Failed downloads: {len(failed_downloads)}")
        
        if downloaded_papers:
            print(f"\nPapers saved to: {agent.downloads_dir}")
            for paper in downloaded_papers:
                print(f"- {paper['filename']}")
    else:
        print("\nSkipping download. Papers URLs have been shown above.")
    
    print(f"\n{'='*60}")
    print("Demo completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    demo_literature_agent()
