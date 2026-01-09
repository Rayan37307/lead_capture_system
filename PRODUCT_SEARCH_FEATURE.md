## Product Search Feature

The Lead Capture System now includes a powerful product search feature that allows customers to search for products directly through the chatbot. This feature is fully integrated with the multi-tenant architecture.

### Features

- **Fuzzy Search**: Uses fuzzy string matching to find relevant products even with typos or partial matches
- **Multi-Tenant Support**: Each tenant has isolated product catalogs
- **Multiple Search Methods**: Search by name, category, brand, or general query
- **Rich Product Information**: Displays product names, prices, descriptions, and images
- **AI Integration**: Seamlessly integrated into the chatbot AI service

### API Endpoints

#### Search Products
```
POST /api/v1/product_search/search
```

Request body:
```json
{
  "query": "search term",
  "tenant_id": "tenant identifier",
  "limit": 10
}
```

#### Get Product by ID
```
GET /api/v1/product_search/product/{product_id}?tenant_id={tenant_id}
```

#### Search by Category
```
GET /api/v1/product_search/category/{category}?tenant_id={tenant_id}&limit={limit}
```

#### Search by Brand
```
GET /api/v1/product_search/brand/{brand}?tenant_id={tenant_id}&limit={limit}
```

### Chatbot Integration

Users can now search for products directly in the chat by using phrases like:
- "Find me a moisturizer"
- "Show me CeraVe products"
- "I'm looking for face cleansers"
- "What do you have for skin care?"

The AI service automatically detects product search queries and responds with relevant product information.

### Configuration

Product data is loaded from JSON files in the `data_center/` directory. Each tenant should have its own JSON file named `{tenant_id}.json`.

### Database Structure

The system uses a multi-tenant architecture with separate database files per tenant:

- **Product Data**: Stored in JSON files in the `data_center/` directory
  - Example: `data_center/shajba.json` contains all products for the 'shajba' tenant
  - Each tenant has their own separate JSON file
  - File naming convention: `{tenant_id}.json`

- **Lead Data**: Stored in SQLite database files in the `tenant_data/` directory
  - Example: `tenant_data/{tenant_id}.db` contains all leads for a specific tenant
  - Each tenant has their own separate SQLite database file
  - File naming convention: `{tenant_id}.db`

### Technical Details

- **Technology**: Uses fuzzywuzzy for fuzzy string matching
- **Architecture**: Modular service design with multi-tenant isolation
- **Data Source**: JSON files for products, SQLite for leads
- **Multi-Tenancy**: Complete data isolation between tenants
- **Performance**: Optimized for fast search results
- **Scalability**: Designed to support multiple tenants independently