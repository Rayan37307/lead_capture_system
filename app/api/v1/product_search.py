from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from app.services.product_search.product_search_service import ProductSearchService
from app.schemas.product_search import ProductSearchRequest, ProductSearchResponse, Product

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize the product search service
product_search_service = ProductSearchService()

@router.post("/search", response_model=ProductSearchResponse)
async def search_products(
    search_request: ProductSearchRequest
):
    """
    Search for products based on query string.
    Requires tenant_id to ensure multi-tenant isolation.
    """
    try:
        logger.info(f"Searching products for tenant: {search_request.tenant_id} with query: {search_request.query}")
        
        # Perform the search
        products = product_search_service.search_products(
            tenant_id=search_request.tenant_id,
            query=search_request.query,
            limit=search_request.limit
        )
        
        # Convert to response format
        product_models = [Product(**product) for product in products]
        
        return ProductSearchResponse(
            products=product_models,
            total=len(product_models),
            query=search_request.query
        )
    except Exception as e:
        logger.error(f"Error searching products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")


@router.get("/product/{product_id}", response_model=Product)
async def get_product_by_id(
    tenant_id: str,
    product_id: str
):
    """
    Get a specific product by its ID.
    Requires tenant_id to ensure multi-tenant isolation.
    """
    try:
        logger.info(f"Getting product {product_id} for tenant: {tenant_id}")
        
        product = product_search_service.get_product_by_id(
            tenant_id=tenant_id,
            product_id=product_id
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return Product(**product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting product: {str(e)}")


@router.get("/category/{category}", response_model=ProductSearchResponse)
async def search_products_by_category(
    tenant_id: str,
    category: str,
    limit: int = Query(default=10, le=50)
):
    """
    Get products by category.
    Requires tenant_id to ensure multi-tenant isolation.
    """
    try:
        logger.info(f"Searching products in category {category} for tenant: {tenant_id}")
        
        products = product_search_service.get_products_by_category(
            tenant_id=tenant_id,
            category=category,
            limit=limit
        )
        
        product_models = [Product(**product) for product in products]
        
        return ProductSearchResponse(
            products=product_models,
            total=len(product_models),
            query=f"category:{category}"
        )
    except Exception as e:
        logger.error(f"Error searching products by category {category}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching products by category: {str(e)}")


@router.get("/brand/{brand}", response_model=ProductSearchResponse)
async def search_products_by_brand(
    tenant_id: str,
    brand: str,
    limit: int = Query(default=10, le=50)
):
    """
    Get products by brand.
    Requires tenant_id to ensure multi-tenant isolation.
    """
    try:
        logger.info(f"Searching products by brand {brand} for tenant: {tenant_id}")
        
        products = product_search_service.get_products_by_brand(
            tenant_id=tenant_id,
            brand=brand,
            limit=limit
        )
        
        product_models = [Product(**product) for product in products]
        
        return ProductSearchResponse(
            products=product_models,
            total=len(product_models),
            query=f"brand:{brand}"
        )
    except Exception as e:
        logger.error(f"Error searching products by brand {brand}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching products by brand: {str(e)}")