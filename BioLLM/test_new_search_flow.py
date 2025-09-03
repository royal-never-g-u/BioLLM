#!/usr/bin/env python3
"""
Test script for New Search Flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.literature_agent import LiteratureAgent

def test_new_search_flow():
    """Test the new search flow: web search -> extract titles/PMIDs -> PubMed API"""
    print("Testing New Search Flow...")
    
    agent = LiteratureAgent()
    
    # Test keywords
    test_keywords = [
        "CRISPR gene editing",
        "metabolic network analysis",
        "E. coli core metabolism"
    ]
    
    for keywords in test_keywords:
        print(f"\n{'='*60}")
        print(f"Testing keywords: {keywords}")
        print(f"{'='*60}")
        
        try:
            # Test the new search flow
            papers = agent.search_papers(keywords, max_results=3)
            
            if papers:
                print(f"Found {len(papers)} papers:")
                for i, paper in enumerate(papers, 1):
                    print(f"\nPaper {i}:")
                    print(f"  Title: {paper.get('title', 'N/A')}")
                    print(f"  Authors: {', '.join(paper.get('authors', [])[:3])}")
                    print(f"  Journal: {paper.get('journal', 'N/A')}")
                    print(f"  PMID: {paper.get('pmid', 'N/A')}")
                    print(f"  DOI: {paper.get('doi', 'N/A')}")
                    print(f"  Source: {paper.get('source', 'N/A')}")
                    print(f"  Full text links: {len(paper.get('fulltext_links', []))}")
                    
                    for link in paper.get('fulltext_links', []):
                        print(f"    {link['type']}: {link['url']}")
            else:
                print("No papers found")
                
        except Exception as e:
            print(f"Error testing {keywords}: {e}")

def test_extract_papers_from_search_results():
    """Test extracting papers from search results"""
    print("\n" + "="*60)
    print("Testing Paper Extraction from Search Results")
    print("="*60)
    
    agent = LiteratureAgent()
    
    # Mock search results
    mock_search_results = """
    Title: CRISPR-Cas9 system: A new-fangled dawn in gene editing
    URL: https://pubmed.ncbi.nlm.nih.gov/31295471/
    
    Title: Metabolic network analysis of pre-ASD newborns
    URL: https://pubmed.ncbi.nlm.nih.gov/38729981/
    
    Title: Gene editing with CRISPR technology
    URL: https://example.com/paper.pdf
    
    Title: E. coli core metabolism and antibiotic resistance
    URL: https://pubmed.ncbi.nlm.nih.gov/33602825/
    """
    
    try:
        extracted_papers = agent._extract_papers_from_search_results(mock_search_results, "CRISPR gene editing")
        
        print(f"Extracted {len(extracted_papers)} papers:")
        for i, paper in enumerate(extracted_papers, 1):
            print(f"\nPaper {i}:")
            print(f"  Title: {paper.get('title', 'N/A')}")
            print(f"  PMID: {paper.get('pmid', 'N/A')}")
            print(f"  Source: {paper.get('source', 'N/A')}")
            
    except Exception as e:
        print(f"Error testing extraction: {e}")

def test_search_pubmed_by_title():
    """Test searching PubMed by title"""
    print("\n" + "="*60)
    print("Testing PubMed Search by Title")
    print("="*60)
    
    agent = LiteratureAgent()
    
    test_titles = [
        "CRISPR-Cas9 system: A new-fangled dawn in gene editing",
        "Metabolic network analysis of pre-ASD newborns",
        "E. coli core metabolism and antibiotic resistance"
    ]
    
    for title in test_titles:
        print(f"\nTesting title: {title}")
        
        try:
            results = agent._search_pubmed_by_title(title)
            
            if results:
                paper = results[0]
                print(f"  Found in PubMed:")
                print(f"    Title: {paper.get('title', 'N/A')}")
                print(f"    Authors: {', '.join(paper.get('authors', [])[:3])}")
                print(f"    PMID: {paper.get('pmid', 'N/A')}")
                print(f"    DOI: {paper.get('doi', 'N/A')}")
            else:
                print("  Not found in PubMed")
                
        except Exception as e:
            print(f"  Error: {e}")

def test_full_workflow():
    """Test the complete workflow"""
    print("\n" + "="*60)
    print("Testing Complete Workflow")
    print("="*60)
    
    agent = LiteratureAgent()
    
    test_keywords = "CRISPR gene editing"
    
    try:
        print(f"Testing complete workflow for: {test_keywords}")
        
        # Step 1: Extract keywords (simulated)
        print("Step 1: Keywords extracted (simulated)")
        
        # Step 2: Search papers using new flow
        print("Step 2: Searching papers using new flow...")
        papers = agent.search_papers(test_keywords, max_results=2)
        
        if papers:
            print(f"Found {len(papers)} papers")
            
            # Step 3: Simulate download process
            print("Step 3: Simulating download process...")
            for i, paper in enumerate(papers, 1):
                print(f"\nProcessing paper {i}: {paper.get('title', 'Unknown')}")
                
                if paper.get('fulltext_links'):
                    print(f"  Found {len(paper['fulltext_links'])} download links")
                    for link in paper['fulltext_links'][:3]:  # Show first 3 links
                        print(f"    {link['type']}: {link['url']}")
                else:
                    print("  No download links found")
        else:
            print("No papers found")
            
    except Exception as e:
        print(f"Error in complete workflow: {e}")

if __name__ == "__main__":
    test_new_search_flow()
    test_extract_papers_from_search_results()
    test_search_pubmed_by_title()
    test_full_workflow()
