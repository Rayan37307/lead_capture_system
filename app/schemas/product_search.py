from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.lead import Message  # Reusing the Message model if needed


class ProductSearchRequest(BaseModel):
    query: str
    tenant_id: str
    limit: int = 10


class Product(BaseModel):
    ID: int
    Type: Optional[str] = Field(alias="Type")
    SKU: Optional[str] = Field(alias="SKU")
    Name: str = Field(alias="Name")
    Published: Optional[int] = Field(alias="Published")
    Is_featured: Optional[int] = Field(default=0, alias="Is featured?")
    Short_description: Optional[str] = Field(alias="Short description")
    Description: Optional[str] = Field(alias="Description")
    In_stock: Optional[int] = Field(alias="In stock?")
    Stock: Optional[str] = Field(alias="Stock")
    Low_stock_amount: Optional[str] = Field(alias="Low stock amount")
    Sale_price: Optional[int] = Field(alias="Sale price")
    Regular_price: Optional[int] = Field(alias="Regular price")
    Categories: Optional[str] = Field(alias="Categories")
    Shipping_class: Optional[str] = Field(alias="Shipping class")
    Images: Optional[str] = Field(alias="Images")
    Brands: Optional[str] = Field(alias="Brands")
    Brand: Optional[str] = Field(alias="Brand")
    Meta_cartflows_redirect_flow_id: Optional[str] = Field(alias="Meta: cartflows_redirect_flow_id")
    Meta_cartflows_add_to_cart_text: Optional[str] = Field(alias="Meta: cartflows_add_to_cart_text")
    Meta_site_sidebar_layout: Optional[str] = Field(alias="Meta: site-sidebar-layout")
    Meta_ast_site_content_layout: Optional[str] = Field(alias="Meta: ast-site-content-layout")
    Meta_site_content_style: Optional[str] = Field(alias="Meta: site-content-style")
    Meta_site_sidebar_style: Optional[str] = Field(alias="Meta: site-sidebar-style")
    Meta_theme_transparent_header_meta: Optional[str] = Field(alias="Meta: theme-transparent-header-meta")
    Meta_astra_migrate_meta_layouts: Optional[str] = Field(alias="Meta: astra-migrate-meta-layouts")
    Meta_stick_header_meta: Optional[str] = Field(alias="Meta: stick-header-meta")
    Meta_uag_css_file_name: Optional[str] = Field(alias="Meta: _uag_css_file_name")
    Meta_uag_js_file_name: Optional[str] = Field(alias="Meta: _uag_js_file_name")
    Meta_last_change_time: Optional[str] = Field(alias="Meta: _last_change_time")
    Meta_wpfoof_identifier_exists: Optional[str] = Field(alias="Meta: wpfoof-identifier_exists")
    Meta_wp_old_date: Optional[str] = Field(alias="Meta: _wp_old_date")
    # Include other fields as needed based on your JSON structure


class ProductSearchResponse(BaseModel):
    products: List[Product]
    total: int
    query: str