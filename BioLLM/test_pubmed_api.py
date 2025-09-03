#!/usr/bin/env python3
"""
Test script for PubMed API Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.literature_agent import LiteratureAgent

def test_pubmed_search():
    """Test PubMed search functionality"""
    print("Testing PubMed Search...")
    
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
            articles = agent._search_pubmed(keywords, max_results=3)
            
            if articles:
                print(f"Found {len(articles)} articles:")
                for i, article in enumerate(articles, 1):
                    print(f"\nArticle {i}:")
                    print(f"  Title: {article.get('title', 'N/A')}")
                    print(f"  Authors: {', '.join(article.get('authors', [])[:3])}")
                    print(f"  Journal: {article.get('journal', 'N/A')}")
                    print(f"  PMID: {article.get('pmid', 'N/A')}")
                    print(f"  DOI: {article.get('doi', 'N/A')}")
                    print(f"  Full text links: {len(article.get('fulltext_links', []))}")
                    
                    for link in article.get('fulltext_links', []):
                        print(f"    {link['type']}: {link['url']}")
            else:
                print("No articles found")
                
        except Exception as e:
            print(f"Error testing {keywords}: {e}")

def test_article_info():
    """Test getting detailed article information"""
    print("\n" + "="*60)
    print("Testing Article Information Retrieval")
    print("="*60)
    
    agent = LiteratureAgent()
    
    # Test with a known PMID
    test_pmids = [
        "12345678",  # Example PMID
        "34567890",  # Example PMID
    ]
    
    for pmid in test_pmids:
        print(f"\nTesting PMID: {pmid}")
        
        try:
            article_info = agent._get_pubmed_article_info(pmid)
            
            if article_info:
                print(f"  Title: {article_info.get('title', 'N/A')}")
                print(f"  Authors: {', '.join(article_info.get('authors', [])[:3])}")
                print(f"  Journal: {article_info.get('journal', 'N/A')}")
                print(f"  DOI: {article_info.get('doi', 'N/A')}")
                print(f"  Full text links: {len(article_info.get('fulltext_links', []))}")
            else:
                print("  No article information found")
                
        except Exception as e:
            print(f"  Error: {e}")

def test_fulltext_links():
    """Test getting full text links"""
    print("\n" + "="*60)
    print("Testing Full Text Link Retrieval")
    print("="*60)
    
    agent = LiteratureAgent()
    
    # Test with a known PMID
    test_pmids = [
        "12345678",  # Example PMID
    ]
    
    for pmid in test_pmids:
        print(f"\nTesting PMID: {pmid}")
        
        try:
            links = agent._get_pubmed_fulltext_links(pmid)
            
            if links:
                print(f"Found {len(links)} full text links:")
                for link in links:
                    print(f"  {link['type']}: {link['url']}")
            else:
                print("No full text links found")
                
        except Exception as e:
            print(f"Error: {e}")

def test_enhanced_search():
    """Test enhanced search with PubMed API"""
    print("\n" + "="*60)
    print("Testing Enhanced Search with PubMed API")
    print("="*60)
    
    agent = LiteratureAgent()
    
    test_keywords = "CRISPR gene editing"
    
    try:
        print(f"Searching for: {test_keywords}")
        papers = agent.search_papers(test_keywords, max_results=3)
        
        if papers:
            print(f"Found {len(papers)} papers:")
            for i, paper in enumerate(papers, 1):
                print(f"\nPaper {i}:")
                print(f"  Title: {paper.get('title', 'N/A')}")
                print(f"  Authors: {', '.join(paper.get('authors', [])[:3])}")
                print(f"  Journal: {paper.get('journal', 'N/A')}")
                print(f"  PMID: {paper.get('pmid', 'N/A')}")
                print(f"  DOI: {paper.get('doi', 'N/A')}")
                print(f"  URLs: {len(paper.get('urls', []))}")
                
                for url_info in paper.get('urls', []):
                    print(f"    {url_info['type']}: {url_info['url']}")
        else:
            print("No papers found")
            
    except Exception as e:
        print(f"Error in enhanced search: {e}")

if __name__ == "__main__":
    test_pubmed_search()
    test_article_info()
    test_fulltext_links()
    test_enhanced_search()
