#!/usr/bin/env python3
"""
Test script for Academic Search Engines
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.literature_agent import LiteratureAgent

def test_arxiv_search():
    """Test arXiv search functionality"""
    print("Testing arXiv Search...")
    
    agent = LiteratureAgent()
    
    test_keywords = [
        "CRISPR gene editing",
        "metabolic network analysis",
        "machine learning biology"
    ]
    
    for keywords in test_keywords:
        print(f"\n{'='*60}")
        print(f"Testing arXiv search for: {keywords}")
        print(f"{'='*60}")
        
        try:
            papers = agent._search_arxiv(keywords, max_results=2)
            
            if papers:
                print(f"Found {len(papers)} papers from arXiv:")
                for i, paper in enumerate(papers, 1):
                    print(f"\nPaper {i}:")
                    print(f"  Title: {paper.get('title', 'N/A')}")
                    print(f"  Authors: {', '.join(paper.get('authors', [])[:3])}")
                    print(f"  arXiv ID: {paper.get('arxiv_id', 'N/A')}")
                    print(f"  DOI: {paper.get('doi', 'N/A')}")
                    print(f"  Published: {paper.get('published_date', 'N/A')}")
                    print(f"  PDF URL: {paper.get('pdf_url', 'N/A')}")
                    print(f"  URLs: {len(paper.get('urls', []))}")
                    
                    for url_info in paper.get('urls', []):
                        print(f"    {url_info['type']}: {url_info['url']}")
            else:
                print("No papers found")
                
        except Exception as e:
            print(f"Error testing arXiv search: {e}")

def test_semantic_scholar_search():
    """Test Semantic Scholar search functionality"""
    print("\n" + "="*60)
    print("Testing Semantic Scholar Search")
    print("="*60)
    
    agent = LiteratureAgent()
    
    test_keywords = [
        "CRISPR gene editing",
        "metabolic network analysis"
    ]
    
    for keywords in test_keywords:
        print(f"\nTesting Semantic Scholar for: {keywords}")
        
        try:
            papers = agent._search_semantic_scholar(keywords, max_results=2)
            
            if papers:
                print(f"Found {len(papers)} papers from Semantic Scholar:")
                for i, paper in enumerate(papers, 1):
                    print(f"\nPaper {i}:")
                    print(f"  Title: {paper.get('title', 'N/A')}")
                    print(f"  Authors: {', '.join(paper.get('authors', [])[:3])}")
                    print(f"  Year: {paper.get('year', 'N/A')}")
                    print(f"  Venue: {paper.get('venue', 'N/A')}")
                    print(f"  DOI: {paper.get('doi', 'N/A')}")
                    print(f"  URLs: {len(paper.get('urls', []))}")
                    
                    for url_info in paper.get('urls', []):
                        print(f"    {url_info['type']}: {url_info['url']}")
            else:
                print("No papers found")
                
        except Exception as e:
            print(f"Error testing Semantic Scholar: {e}")

def test_crossref_search():
    """Test Crossref search functionality"""
    print("\n" + "="*60)
    print("Testing Crossref Search")
    print("="*60)
    
    agent = LiteratureAgent()
    
    test_keywords = [
        "CRISPR gene editing",
        "metabolic network analysis"
    ]
    
    for keywords in test_keywords:
        print(f"\nTesting Crossref for: {keywords}")
        
        try:
            papers = agent._search_crossref(keywords, max_results=2)
            
            if papers:
                print(f"Found {len(papers)} papers from Crossref:")
                for i, paper in enumerate(papers, 1):
                    print(f"\nPaper {i}:")
                    print(f"  Title: {paper.get('title', 'N/A')}")
                    print(f"  Authors: {', '.join(paper.get('authors', [])[:3])}")
                    print(f"  Year: {paper.get('year', 'N/A')}")
                    print(f"  Journal: {paper.get('journal', 'N/A')}")
                    print(f"  DOI: {paper.get('doi', 'N/A')}")
                    print(f"  URLs: {len(paper.get('urls', []))}")
                    
                    for url_info in paper.get('urls', []):
                        print(f"    {url_info['type']}: {url_info['url']}")
            else:
                print("No papers found")
                
        except Exception as e:
            print(f"Error testing Crossref: {e}")

def test_combined_search():
    """Test combined search from all academic sources"""
    print("\n" + "="*60)
    print("Testing Combined Academic Search")
    print("="*60)
    
    agent = LiteratureAgent()
    
    test_keywords = "CRISPR gene editing"
    
    try:
        print(f"Testing combined search for: {test_keywords}")
        
        papers = agent.search_papers(test_keywords, max_results=5)
        
        if papers:
            print(f"\nFound {len(papers)} papers from all sources:")
            for i, paper in enumerate(papers, 1):
                print(f"\nPaper {i}:")
                print(f"  Title: {paper.get('title', 'N/A')}")
                print(f"  Authors: {', '.join(paper.get('authors', [])[:3])}")
                print(f"  Source: {paper.get('source', 'N/A')}")
                print(f"  Year: {paper.get('year', 'N/A')}")
                print(f"  DOI: {paper.get('doi', 'N/A')}")
                print(f"  URLs: {len(paper.get('urls', []))}")
                
                for url_info in paper.get('urls', [])[:3]:  # Show first 3 URLs
                    print(f"    {url_info['type']}: {url_info['url']}")
        else:
            print("No papers found")
            
    except Exception as e:
        print(f"Error in combined search: {e}")

def test_duplicate_removal():
    """Test duplicate removal functionality"""
    print("\n" + "="*60)
    print("Testing Duplicate Removal")
    print("="*60)
    
    agent = LiteratureAgent()
    
    # Mock papers with duplicates
    mock_papers = [
        {
            'title': 'CRISPR gene editing technology',
            'doi': '10.1234/test.1',
            'source': 'arXiv'
        },
        {
            'title': 'CRISPR gene editing technology',
            'doi': '10.1234/test.1',
            'source': 'Semantic Scholar'
        },
        {
            'title': 'New advances in CRISPR technology',
            'doi': '10.1234/test.2',
            'source': 'Crossref'
        },
        {
            'title': 'CRISPR gene editing technology review',
            'doi': '',
            'source': 'PubMed'
        }
    ]
    
    try:
        unique_papers = agent._remove_duplicate_papers(mock_papers)
        
        print(f"Original papers: {len(mock_papers)}")
        print(f"After duplicate removal: {len(unique_papers)}")
        
        for i, paper in enumerate(unique_papers, 1):
            print(f"\nPaper {i}:")
            print(f"  Title: {paper.get('title', 'N/A')}")
            print(f"  DOI: {paper.get('doi', 'N/A')}")
            print(f"  Source: {paper.get('source', 'N/A')}")
            
    except Exception as e:
        print(f"Error testing duplicate removal: {e}")

def test_paper_ranking():
    """Test paper ranking functionality"""
    print("\n" + "="*60)
    print("Testing Paper Ranking")
    print("="*60)
    
    agent = LiteratureAgent()
    
    # Mock papers for ranking
    mock_papers = [
        {
            'title': 'CRISPR gene editing in bacteria',
            'abstract': 'This paper discusses CRISPR gene editing technology in bacterial systems',
            'source': 'arXiv',
            'year': 2023
        },
        {
            'title': 'Machine learning applications',
            'abstract': 'This paper discusses machine learning in various applications',
            'source': 'Semantic Scholar',
            'year': 2022
        },
        {
            'title': 'CRISPR technology advances',
            'abstract': 'Recent advances in CRISPR gene editing technology',
            'source': 'Crossref',
            'year': 2024
        }
    ]
    
    try:
        keywords = "CRISPR gene editing"
        ranked_papers = agent._rank_papers_by_relevance(mock_papers, keywords)
        
        print(f"Ranked papers for keywords: {keywords}")
        for i, paper in enumerate(ranked_papers, 1):
            print(f"\nRank {i}:")
            print(f"  Title: {paper.get('title', 'N/A')}")
            print(f"  Source: {paper.get('source', 'N/A')}")
            print(f"  Year: {paper.get('year', 'N/A')}")
            
    except Exception as e:
        print(f"Error testing paper ranking: {e}")

if __name__ == "__main__":
    test_arxiv_search()
    test_semantic_scholar_search()
    test_crossref_search()
    test_combined_search()
    test_duplicate_removal()
    test_paper_ranking()
