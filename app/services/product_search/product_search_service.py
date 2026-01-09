import json
import os
from typing import List, Dict, Any, Optional
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

logger = logging.getLogger(__name__)

class ProductSearchService:
    """
    A modular product search service that works with multi-tenant architecture.
    Loads product data from JSON files and provides search functionality.
    """
    
    def __init__(self, data_directory: str = "data_center"):
        """
        Initialize the product search service.
        
        Args:
            data_directory: Directory where product JSON files are stored
        """
        self.data_directory = data_directory
        self.tenant_products = {}
        self.load_all_tenant_products()
    
    def load_all_tenant_products(self):
        """Load product data for all tenants from JSON files."""
        if not os.path.exists(self.data_directory):
            logger.warning(f"Data directory {self.data_directory} does not exist")
            return
        
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.json'):
                tenant_id = filename.replace('.json', '')
                file_path = os.path.join(self.data_directory, filename)
                self.tenant_products[tenant_id] = self.load_products_from_file(file_path)
    
    def load_products_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load products from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing products
            
        Returns:
            List of product dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                products = json.load(file)
                logger.info(f"Loaded {len(products)} products from {file_path}")
                return products
        except Exception as e:
            logger.error(f"Error loading products from {file_path}: {e}")
            return []
    
    def get_products_for_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get products for a specific tenant.
        
        Args:
            tenant_id: The tenant identifier
            
        Returns:
            List of products for the tenant
        """
        return self.tenant_products.get(tenant_id, [])
    
    def search_products(self, tenant_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for products based on a query string.
        
        Args:
            tenant_id: The tenant identifier
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching products
        """
        products = self.get_products_for_tenant(tenant_id)
        if not products:
            logger.warning(f"No products found for tenant {tenant_id}")
            return []
        
        # Normalize the query
        query = query.lower().strip()
        if not query:
            return products[:limit]
        
        # Perform fuzzy search on product names and descriptions
        scored_products = []
        for product in products:
            product_name = product.get('Name', '').lower()
            product_description = product.get('Description', '').lower()
            product_categories = product.get('Categories', '').lower()
            
            # Calculate fuzzy match scores
            name_score = fuzz.partial_ratio(query, product_name)
            description_score = fuzz.partial_ratio(query, product_description)
            category_score = fuzz.partial_ratio(query, product_categories)
            
            # Use the highest score
            max_score = max(name_score, description_score, category_score)
            
            # Only include products with a reasonable match score
            if max_score > 30:  # Threshold for relevance
                scored_products.append((product, max_score))
        
        # Sort by score (descending) and return top results
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [product for product, score in scored_products[:limit]]
    
    def get_product_by_id(self, tenant_id: str, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific product by its ID.
        
        Args:
            tenant_id: The tenant identifier
            product_id: The product ID
            
        Returns:
            Product dictionary or None if not found
        """
        products = self.get_products_for_tenant(tenant_id)
        for product in products:
            if str(product.get('ID')) == str(product_id):
                return product
        return None
    
    def get_products_by_category(self, tenant_id: str, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get products by category.
        
        Args:
            tenant_id: The tenant identifier
            category: Category to search for
            limit: Maximum number of results to return
            
        Returns:
            List of products in the category
        """
        products = self.get_products_for_tenant(tenant_id)
        category_lower = category.lower()
        
        matching_products = []
        for product in products:
            product_categories = product.get('Categories', '').lower()
            if category_lower in product_categories:
                matching_products.append(product)
        
        return matching_products[:limit]
    
    def get_products_by_brand(self, tenant_id: str, brand: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get products by brand.
        
        Args:
            tenant_id: The tenant identifier
            brand: Brand to search for
            limit: Maximum number of results to return
            
        Returns:
            List of products from the brand
        """
        products = self.get_products_for_tenant(tenant_id)
        brand_lower = brand.lower()
        
        matching_products = []
        for product in products:
            product_brand = product.get('Brand', '').lower()
            if brand_lower in product_brand:
                matching_products.append(product)
        
        return matching_products[:limit]
    
    def format_product_response(self, product: Dict[str, Any]) -> str:
        """
        Format a product for chatbot response.
        
        Args:
            product: Product dictionary
            
        Returns:
            Formatted string representation of the product
        """
        name = product.get('Name', 'N/A')
        price = product.get('Sale price', product.get('Regular price', 'N/A'))
        description = product.get('Description', 'No description available')
        brand = product.get('Brand', 'N/A')
        
        # Truncate description if too long
        if len(description) > 200:
            description = description[:200] + "..."
        
        formatted = f"""
Product: {name}
Brand: {brand}
Price: {price}
Description: {description}
        """.strip()
        
        return formatted