#!/usr/bin/env python3
"""
Test script for Page Traversal and PDF Finding Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.literature_agent import LiteratureAgent

def test_pdf_link_finding():
    """Test PDF link finding functionality"""
    print("Testing PDF Link Finding...")
    
    agent = LiteratureAgent()
    
    # Test URLs (these are example URLs that might contain PDF links)
    test_urls = [
        "https://www.nature.com/articles/s41598-023-12345-6",  # Nature article
        "https://www.sciencedirect.com/science/article/pii/S2001037021003354",  # ScienceDirect
        "https://pubmed.ncbi.nlm.nih.gov/12345678/",  # PubMed
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print(f"{'='*60}")
        
        try:
            pdf_links = agent._find_pdf_links(url)
            
            if pdf_links:
                print(f"Found {len(pdf_links)} potential PDF links:")
                for i, link in enumerate(pdf_links, 1):
                    print(f"  {i}. URL: {link['url']}")
                    print(f"     Text: {link['text'][:100]}...")
                    print(f"     Href: {link['href']}")
            else:
                print("No PDF links found")
                
        except Exception as e:
            print(f"Error testing {url}: {e}")

def test_pdf_url_detection():
    """Test PDF URL detection"""
    print("\n" + "="*60)
    print("Testing PDF URL Detection")
    print("="*60)
    
    agent = LiteratureAgent()
    
    test_urls = [
        "https://example.com/paper.pdf",
        "https://example.com/paper.PDF",
        "https://example.com/paper?format=pdf",
        "https://example.com/paper",
        "https://example.com/paper.html",
    ]
    
    for url in test_urls:
        try:
            is_pdf = agent._is_pdf_url(url)
            print(f"{url}: {'PDF' if is_pdf else 'Not PDF'}")
        except Exception as e:
            print(f"{url}: Error - {e}")

def test_download_from_page():
    """Test downloading from page functionality"""
    print("\n" + "="*60)
    print("Testing Download from Page")
    print("="*60)
    
    agent = LiteratureAgent()
    
    # Test with a real URL that might have PDF links
    test_url = "https://www.nature.com/articles/s41598-023-12345-6"
    
    try:
        print(f"Testing download from page: {test_url}")
        result = agent._download_from_page(test_url, "test_paper.pdf")
        
        print(f"Result: {result}")
        
        if result['success']:
            print(f"✓ Successfully downloaded: {result['filename']}")
            print(f"  File path: {result['file_path']}")
            print(f"  Original URL: {result.get('original_url', 'N/A')}")
            print(f"  PDF URL: {result.get('pdf_url', 'N/A')}")
        else:
            print(f"✗ Download failed: {result['message']}")
            
    except Exception as e:
        print(f"Error testing download from page: {e}")

def test_full_download_process():
    """Test the full download process"""
    print("\n" + "="*60)
    print("Testing Full Download Process")
    print("="*60)
    
    agent = LiteratureAgent()
    
    # Test URLs that might be HTML pages with PDF links
    test_urls = [
        "https://www.nature.com/articles/s41598-023-12345-6",
        "https://www.sciencedirect.com/science/article/pii/S2001037021003354",
    ]
    
    for url in test_urls:
        print(f"\nTesting full download process for: {url}")
        
        try:
            result = agent.download_paper(url, f"test_paper_{int(time.time())}.pdf")
            
            print(f"Result: {result}")
            
            if result['success']:
                print(f"✓ Successfully downloaded: {result['filename']}")
            else:
                print(f"✗ Download failed: {result['message']}")
                
        except Exception as e:
            print(f"Error in full download process: {e}")

if __name__ == "__main__":
    import time
    
    test_pdf_link_finding()
    test_pdf_url_detection()
    test_download_from_page()
    test_full_download_process()
