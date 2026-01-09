# Plan for Multi-Tenant Product Search System

This document outlines the complete plan for building an efficient, secure, and dynamic multi-tenant system for searching product details.

## 1. Goal

The objective is to create a RAG-like (Retrieval-Augmented Generation) system that can answer user queries about products. The system must be multi-tenant, meaning each tenant's product data is kept completely separate and secure.

## 2. Core Technology and Architecture

### 2.1. Database Selection: SQLite

We will use **SQLite** as the database engine.

*   **Why SQLite?**
    *   **Lightweight & Serverless:** It runs directly within the application with no separate server process to manage.
    *   **File-Based:** The entire database is a single file, making it easy to manage and isolate tenant data.
    *   **Zero-Configuration:** No complex setup is needed.
    *   **Free & Reliable:** It's public domain, costs nothing, and is one of the most deployed database engines in the world.
    *   **Python Native:** Python has built-in support via the `sqlite3` module.

### 2.2. Multi-Tenancy Architecture: One Database Per Tenant

This is the most critical architectural decision for ensuring security and data isolation.

*   **Approach:** We will create a separate SQLite database file for each tenant.
*   **Implementation:** Database files will be named based on the tenant's unique ID (e.g., `tenant_data/{tenant_id}.db`).
*   **Justification:** This physically separates data, making it impossible for one tenant's queries to access another tenant's information. It is the most robust and secure model for multi-tenancy.

## 3. Step-by-Step Implementation Plan

### Phase 1: Project Setup

1.  **Create Data Directory:** A new directory named `tenant_data/` will be created in the project root to store the SQLite database files for each tenant.
2.  **Update `.gitignore`:** The `tenant_data/` directory will be added to the `.gitignore` file to ensure that no tenant data is ever committed to the version control repository.
3.  **Analyze Data Schema:**
    *   **Action Item:** You will provide a sample of the `products.json` file.
    *   Based on the sample, we will define the schema for the `products` table in the database. For example:
        ```sql
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            category TEXT,
            image_url TEXT
        );
        ```

### Phase 2: Database Management Module

A new module, `app/database/product_db.py`, will be created to handle all database interactions.

1.  **`get_db_path(tenant_id: str)`:** A helper function to return the path to a tenant's database file.
2.  **`get_db_connection(tenant_id: str)`:** This function will connect to the appropriate tenant database (using the path from the helper function) and return a SQLite connection object. It will create the database file and its parent directory if they don't exist.
3.  **`initialize_database(tenant_id: str)`:** This function will use the connection to execute the `CREATE TABLE` statement defined in Phase 1, ensuring the `products` table exists for a given tenant.

### Phase 3: Dynamic Data Ingestion

We will create a new API endpoint to allow for dynamic creation and updating of a tenant's product catalog.

1.  **Create API Endpoint:** Define a new endpoint: `POST /api/v1/products/{tenant_id}`.
2.  **Endpoint Logic:** The function handling this endpoint will:
    a. Accept a JSON array of product objects in the request body.
    b. Call `initialize_database(tenant_id)` to ensure the database and table are ready.
    c. **(Optional: For Updates)** Delete all existing records from the `products` table for that tenant.
    d. Iterate through the product objects from the request and execute SQL `INSERT` statements to populate the tenant's `products` table.
    e. Return a success message with the number of products loaded.

### Phase 4: The Query Engine (Retriever)

In the `app/database/product_db.py` module, we will create the functions for searching and retrieving product data. **Every function will require a `tenant_id` to ensure it connects to the correct database.**

*   **`search_products_by_keyword(tenant_id: str, keyword: str) -> list[dict]`:** Searches product names and descriptions for a keyword.
*   **`get_product_by_id(tenant_id: str, product_id: str) -> dict | None`:** Retrieves a single product by its exact ID.
*   *(Additional functions can be added as needed, e.g., `get_products_by_category`).*

### Phase 5: Integration with Services (RAG)

The existing application services will be modified to use the new product query engine.

1.  **Identify Service:** A service like `app/services/ai_service.py` or `lead_service.py` will be chosen to handle product-related queries.
2.  **Update Service Logic:** When a user message is being processed, the service will:
    a. **Detect Intent:** Determine if the user is asking about a product.
    b. **Retrieve:** If it's a product query, call the appropriate function from `product_db.py` (e.g., `search_products_by_keyword`) using the correct `tenant_id` to fetch relevant product data.
    c. **Augment:** Format the retrieved product data and insert it into a prompt for the AI model. Example prompt: `"Based on the following product information, answer the user's question. Products: [...]. User's question: '...'"`
    d. **Generate:** Send the augmented prompt to the language model to get a natural language response.
    e. **Respond:** Send the AI's generated response back to the user.

## 4. Next Steps

1.  **You provide a sample of your JSON product data.**
2.  Based on the sample, I will begin implementing **Phase 1** and **Phase 2**.
