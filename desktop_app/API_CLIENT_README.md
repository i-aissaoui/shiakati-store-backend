# Shiakati Store API Client Guide

## Overview

This document explains how the desktop application connects to the backend API.

## Key Features of the API Client

1. **Built-in Variant Support**: The API client now properly handles product variants with different sizes and colors.

2. **Field Name Transformation**: Automatically maps API field names to UI expectations:
   - `name` → `product_name`  
   - `quantity` → `stock`

3. **Auto-login Capability**: Can automatically authenticate with default credentials.

4. **Fallback Mechanism**: Generates dummy data when the backend is unavailable.

## How to Use the API Client

The API client is available through the `src.utils.api_client.APIClient` class. It already contains all the methods needed for the desktop application.

### Key Methods

- `get_inventory()`: Returns product inventory with proper variant handling
- `get_inventory_safe()`: Safe wrapper for get_inventory
- `get_combined_inventory()`: Fetches both products and variants with field transformation

### Running the Application

Two run scripts are provided:

1. **Regular Mode** (with external patches):
   ```bash
   python main.py
   ```

2. **Direct Mode** (using built-in methods without patches):
   ```bash
   python main_direct.py
   ```

## Database Schema

The application works with the following key tables:

- **products**: Contains base product information (name, description, category_id)
- **variants**: Contains variant information (size, color, barcode, price, quantity) 
- **categories**: Contains product categories

## Troubleshooting

If you see errors about missing attributes:

1. Check that you're using the latest API client implementation
2. Verify the backend API server is running
3. Look for any auth errors in the console output
