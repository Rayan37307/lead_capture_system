#!/usr/bin/env python3
"""
Test script for the product search functionality
"""
import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, '/home/rayan/coding/lead_capture_system')

from app.services.product_search.product_search_service import ProductSearchService

async def test_product_search():
    print("Testing Product Search Service...")
    
    # Initialize the service
    service = ProductSearchService()
    
    # Test loading products
    print("\n1. Testing product loading...")
    tenant_products = service.get_products_for_tenant('shajba')
    print(f"Loaded {len(tenant_products)} products for tenant 'shajba'")
    
    if not tenant_products:
        print("ERROR: No products loaded!")
        return
    
    # Test searching for a product
    print("\n2. Testing product search...")
    search_results = service.search_products('shajba', 'CeraVe', limit=5)
    print(f"Found {len(search_results)} products matching 'CeraVe':")
    for i, product in enumerate(search_results[:3], 1):  # Show first 3
        print(f"  {i}. {product['Name']} - Price: {product.get('Sale price', product.get('Regular price', 'N/A'))}")
    
    # Test getting a specific product
    print("\n3. Testing product retrieval by ID...")
    if tenant_products:
        sample_product_id = str(tenant_products[0]['ID'])
        product = service.get_product_by_id('shajba', sample_product_id)
        if product:
            print(f"Retrieved product: {product['Name']}")
        else:
            print("Product not found by ID")
    
    # Test category search
    print("\n4. Testing category search...")
    category_results = service.get_products_by_category('shajba', 'Skin', limit=3)
    print(f"Found {len(category_results)} products in 'Skin' category:")
    for i, product in enumerate(category_results, 1):
        print(f"  {i}. {product['Name']}")
    
    # Test brand search
    print("\n5. Testing brand search...")
    brand_results = service.get_products_by_brand('shajba', 'CeraVe', limit=3)
    print(f"Found {len(brand_results)} products from 'CeraVe' brand:")
    for i, product in enumerate(brand_results, 1):
        print(f"  {i}. {product['Name']} - {product['Brand']}")
    
    print("\n6. Testing product formatting...")
    if brand_results:
        formatted = service.format_product_response(brand_results[0])
        print("Formatted product response:")
        print(formatted)
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_product_search())