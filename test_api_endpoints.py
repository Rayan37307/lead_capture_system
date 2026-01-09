#!/usr/bin/env python3
"""
Test script for the product search API endpoints
"""
import asyncio
import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, '/home/rayan/coding/lead_capture_system')

from fastapi.testclient import TestClient
from app.main import app

def test_api_endpoints():
    print("Testing Product Search API Endpoints...")
    
    client = TestClient(app)
    
    # Test the search endpoint
    print("\n1. Testing POST /api/v1/product_search/search")
    response = client.post("/api/v1/product_search/search", json={
        "query": "CeraVe",
        "tenant_id": "shajba",
        "limit": 3
    })
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} products matching 'CeraVe'")
        for i, product in enumerate(data['products'][:2], 1):  # Show first 2
            print(f"  {i}. {product['Name']} - Price: {product.get('Sale price', product.get('Regular price', 'N/A'))}")
    else:
        print(f"Error: {response.text}")
    
    # Test the get product by ID endpoint
    print("\n2. Testing GET /api/v1/product_search/product/{id}")
    # First, let's get a product ID from the previous search
    if response.status_code == 200 and data['products']:
        product_id = data['products'][0]['ID']
        response2 = client.get(f"/api/v1/product_search/product/{product_id}?tenant_id=shajba")
        print(f"Status Code: {response2.status_code}")
        if response2.status_code == 200:
            product = response2.json()
            print(f"Retrieved product: {product['Name']}")
        else:
            print(f"Error retrieving product: {response2.text}")
    
    # Test the category search endpoint
    print("\n3. Testing GET /api/v1/product_search/category/{category}")
    response3 = client.get("/api/v1/product_search/category/Skin?tenant_id=shajba&limit=3")
    print(f"Status Code: {response3.status_code}")
    if response3.status_code == 200:
        data3 = response3.json()
        print(f"Found {data3['total']} products in 'Skin' category")
        for i, product in enumerate(data3['products'], 1):
            print(f"  {i}. {product['Name']}")
    else:
        print(f"Error: {response3.text}")
    
    # Test the brand search endpoint
    print("\n4. Testing GET /api/v1/product_search/brand/{brand}")
    response4 = client.get("/api/v1/product_search/brand/CeraVe?tenant_id=shajba&limit=3")
    print(f"Status Code: {response4.status_code}")
    if response4.status_code == 200:
        data4 = response4.json()
        print(f"Found {data4['total']} products from 'CeraVe' brand")
        for i, product in enumerate(data4['products'], 1):
            print(f"  {i}. {product['Name']} - {product['Brand']}")
    else:
        print(f"Error: {response4.text}")
    
    print("\nAll API endpoint tests completed!")

if __name__ == "__main__":
    test_api_endpoints()