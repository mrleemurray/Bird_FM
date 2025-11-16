#!/usr/bin/env python3
"""
Test script to debug Xeno-Canto API calls
Run this to test different query formats and see what works
"""

import requests
import json
import sys
from urllib.parse import quote

def test_api_call(query, api_key=None):
    """Test an API call with the given query"""
    base_url = 'https://xeno-canto.org/api/3/recordings'  # Updated to API v3
    
    # Try different URL formats
    urls = [
        f'{base_url}?query={quote(query)}',
    ]
    
    if api_key:
        urls.append(f'{base_url}?query={quote(query)}&key={api_key}')
    
    for url in urls:
        print(f"\n{'='*70}")
        print(f"Testing: {url}")
        print('='*70)
        
        try:
            headers = {
                'User-Agent': 'BirdFM/1.0 Test Script'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"Number of recordings: {data.get('numRecordings', 0)}")
                print(f"Number of species: {data.get('numSpecies', 0)}")
                
                if 'recordings' in data and len(data['recordings']) > 0:
                    first = data['recordings'][0]
                    print(f"\nFirst recording:")
                    print(f"  ID: {first.get('id', 'N/A')}")
                    print(f"  Species: {first.get('en', 'N/A')}")
                    print(f"  Location: {first.get('loc', 'N/A')}")
                    print(f"  Country: {first.get('cnt', 'N/A')}")
                    if 'file' in first:
                        print(f"  Audio file URL: {first['file']}")
                    if 'file-name' in first:
                        print(f"  Filename: {first['file-name']}")
                    if 'sono' in first:
                        print(f"  Sonogram data available: Yes")
                        if 'small' in first['sono']:
                            print(f"  Sono small: {first['sono']['small']}")
                
                return True
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    return False

if __name__ == "__main__":
    print("Xeno-Canto API Test Script")
    print("="*70)
    
    # Get API key from command line if provided
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    if api_key:
        print(f"Using API key: {api_key[:10]}...")
    else:
        print("No API key provided (testing without authentication)")
    
    # Test different query formats
    test_queries = [
        'cnt:"United Kingdom"',
        'cnt:uk',
        'Australia',
        'cnt:Australia',
        'gen:Turdus',  # Try a genus search
    ]
    
    print("\nTesting different query formats...")
    
    for query in test_queries:
        if test_api_call(query, api_key):
            print(f"\n✅ Working query format: {query}")
            break
    else:
        print("\n❌ None of the query formats worked!")
        print("\nPlease check:")
        print("1. Is the Xeno-Canto API accessible from your location?")
        print("2. Try visiting https://xeno-canto.org/api/3/recordings?query=cnt:uk in a browser")
        print("3. Check if you need an API key and it's valid")
