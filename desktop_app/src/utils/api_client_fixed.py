#!/usr/bin/env python3
# filepath: /home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/utils/api_client_fixed.py

"""
Fixed version of the API client with syntax error corrected.
This file is a temporary solution to fix the syntax error in the original api_client.py.
"""

# Import all necessary modules
import requests
import json
import random
import time
import datetime
import uuid
from typing import Dict, Any, List, Optional

class APIClient:
    """API client for Shiakati Store backend."""
    
    def __init__(self):
        """Initialize the API client."""
        self.base_url = "http://localhost:8000"
        self.token = None
        
        # Configure requests session with default timeout and retries
        self.session = requests.Session()
        retries = requests.adapters.Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
        
        # Add caching for better performance
        self._cache = {}
        self._cache_timeout = {}
        self._default_cache_timeout = 60  # Default cache timeout in seconds
    
    def login(self, username: str, password: str) -> bool:
        """Login to the API and get authentication token."""
        try:
            print(f"Logging in as {username}...")
            response = self.session.post(
                f"{self.base_url}/token", 
                data={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"Login successful, token received")
                return True
            else:
                print(f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for authenticated API requests."""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication token."""
        if not self.token:
            print("No token available, attempting auto-login...")
            return self.login("admin", "123")
        return True
    
    def _handle_auth_error(self, response) -> bool:
        """Handle authentication errors by refreshing token."""
        if response.status_code == 401:
            print("Authentication error, attempting to re-authenticate...")
            return self.login("admin", "123")
        return False
    
    def clear_cache(self, prefix: str = None):
        """Clear cache entries with the given prefix."""
        if prefix:
            keys_to_clear = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_clear:
                self._cache.pop(key, None)
                self._cache_timeout.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timeout.clear()
    
    def transform_product_fields(self, products):
        """Transform product field names from API format to UI format."""
        transformed_products = []
        
        for product in products:
            # Create a new dict with the transformed field names
            transformed = {
                # Map 'name' to 'product_name' which is expected by the UI
                "product_name": product.get("name", "Unknown Product"),
                
                # Keep 'barcode' field as is or generate one from product ID
                "barcode": product.get("barcode", f"SKU{product.get('id', '')}"),
                
                # Keep 'price' field as is
                "price": product.get("price", 0),
                
                # Map 'quantity' or 'inventory' to 'stock' expected by the UI
                "stock": product.get("quantity", product.get("inventory", product.get("total_stock", 0))),
                
                # Keep all original fields too
                **product
            }
            transformed_products.append(transformed)
            
        return transformed_products
    
    def get_combined_inventory(self):
        """Get inventory combining variants and products data for a complete view."""
        try:
            # Check cache first
            cache_key = "inventory_data"
            if cache_key in self._cache and (time.time() - self._cache_timeout.get(cache_key, 0)) < 300:
                print("Using cached inventory data")
                return self._cache[cache_key]
            
            # Check if we need to auto-login
            if not self._ensure_authenticated():
                print("Authentication failed for inventory")
                return []
                
            # First get all products
            products_response = self.session.get(
                f"{self.base_url}/products", 
                headers=self.get_headers(),
                timeout=10
            )
            
            if products_response.status_code != 200:
                print(f"Failed to get products: {products_response.status_code}")
                return []
                
            products = products_response.json()
            print(f"Retrieved {len(products)} products")
            
            # Create a product lookup map
            products_map = {product["id"]: product for product in products}
            
            # Get all variants
            variants_response = self.session.get(
                f"{self.base_url}/variants", 
                headers=self.get_headers(),
                timeout=10
            )
            
            inventory_items = []
            
            if variants_response.status_code == 200:
                variants = variants_response.json()
                print(f"Retrieved {len(variants)} variants")
                
                # Process each variant and associate with its product
                for variant in variants:
                    product_id = variant.get("product_id")
                    if product_id in products_map:
                        product = products_map[product_id]
                        item = {
                            # Core fields expected by UI
                            "product_name": f"{product.get('name', 'Unknown')} - {variant.get('color', '')} ({variant.get('size', '')})",
                            "barcode": variant.get("barcode", f"SKU{variant.get('id', '')}"),
                            "price": variant.get("price", 0),
                            "stock": variant.get("quantity", 0),
                            
                            # Keep variant fields
                            "variant_id": variant.get("id"),
                            "size": variant.get("size", ""),
                            "color": variant.get("color", ""),
                            
                            # Keep product fields
                            "product_id": product_id,
                            "category": product.get("category_name", ""),
                            "description": product.get("description", ""),
                        }
                        inventory_items.append(item)
                
                # If we found variants, store in cache and return them
                if inventory_items:
                    self._cache[cache_key] = inventory_items
                    self._cache_timeout[cache_key] = time.time()
                    return inventory_items
            
            # If no variants or error getting variants, transform products directly
            transformed = self.transform_product_fields(products)
            self._cache[cache_key] = transformed
            self._cache_timeout[cache_key] = time.time()
            return transformed
            
        except Exception as e:
            print(f"Error in get_combined_inventory: {e}")
            return []
    
    def get_inventory(self):
        """Get all products data with field name transformation."""
        return self.get_combined_inventory()
    
    def get_inventory_safe(self):
        """Safe wrapper for get_inventory with field transformation."""
        try:
            return self.get_inventory()
        except Exception as e:
            print(f"Error in get_inventory_safe: {e}")
            return []
    
    def get_categories(self):
        """Get list of product categories."""
        try:
            # Check if we need to auto-login
            if not self._ensure_authenticated():
                print("Authentication failed for categories")
                return []
                
            response = self.session.get(
                f"{self.base_url}/categories", 
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                categories = response.json()
                
                # Ensure proper format expected by UI
                formatted_categories = []
                for category in categories:
                    formatted_categories.append({
                        "id": category.get("id"),
                        "name": category.get("name", "Unknown category"),
                        "description": category.get("description", "")
                    })
                return formatted_categories
            
            print(f"Could not get categories (status {response.status_code})")
            return []
        except Exception as e:
            print(f"Error in get_categories: {e}")
            return []
    
    def get_expenses(self):
        """Get all expenses with improved error handling and authentication."""
        try:
            # Check if we need to auto-login
            if not self._ensure_authenticated():
                print("Authentication failed for expenses")
                return []
                
            response = self.session.get(
                f"{self.base_url}/expenses", 
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                expenses = response.json()
                return expenses
            
            print(f"Could not get expenses (status {response.status_code})")
            return []
        except Exception as e:
            print(f"Error in get_expenses: {e}")
            return []
    
    def get_expenses_safely(self):
        """Safe wrapper for get_expenses."""
        return self.get_expenses()
    
    def get_sales_history(self):
        """Get list of all sales with their details for history view."""
        try:
            if not self._ensure_authenticated():
                print("Authentication failed for sales history")
                return []
                
            # Try to get from the API
            response = self.session.get(
                f"{self.base_url}/sales", 
                headers=self.get_headers(),
                timeout=30
            )
            if response.status_code == 200:
                sales = response.json()
                print(f"Retrieved {len(sales)} sales from API")
                return sales
            else:
                print(f"Error getting sales history: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in get_sales_history: {str(e)}")
            return []
    
    def get_sale_details(self, sale_id: str):
        """Get details for a specific sale."""
        try:
            print(f"Getting detailed information for sale {sale_id}")
            
            # Check cache first
            cache_key = f"sale_{sale_id}"
            if cache_key in self._cache and (time.time() - self._cache_timeout.get(cache_key, 0)) < 300:
                print(f"Found sale {sale_id} in cache")
                return self._cache[cache_key]
            
            # Try to get from the API
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get sale details")
                return None
                
            response = self.session.get(
                f"{self.base_url}/sales/{sale_id}", 
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                sale = response.json()
                print(f"Retrieved sale {sale_id} details from API")
                
                # Save in cache
                self._cache[cache_key] = sale
                self._cache_timeout[cache_key] = time.time()
                
                return sale
            elif response.status_code == 404:
                print(f"Sale {sale_id} not found")
                return None
            else:
                print(f"Error retrieving sale: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_sale_details: {str(e)}")
            return None
    
    def get_orders(self):
        """Get all orders with their details."""
        try:
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get orders")
                return []
                
            response = self.session.get(f"{self.base_url}/orders", headers=self.get_headers(), timeout=30)
            if response.status_code != 200:
                print(f"Error getting orders: {response.status_code}")
                return []

            orders = response.json()
            if not orders:
                print("No orders found")
                return []

            print(f"Processing {len(orders)} orders...")
            
            formatted_orders = []
            for order in orders:
                try:
                    formatted_order = {
                        "id": order.get("id", ""),
                        "order_time": order.get("order_time", ""),
                        "customer_name": order.get("customer_name", "Unknown"),
                        "phone_number": order.get("phone_number", "N/A"),
                        "total": float(order.get("total", 0)),
                        "status": order.get("status", "pending"),
                        "delivery_method": order.get("delivery_method", "N/A"),
                        "wilaya": order.get("wilaya", "N/A"),
                        "commune": order.get("commune", "N/A"),
                        "notes": order.get("notes", ""),
                        "items": order.get("items", [])
                    }
                    formatted_orders.append(formatted_order)
                except Exception as item_error:
                    print(f"Error processing order: {str(item_error)}")
                    continue

            return formatted_orders

        except Exception as e:
            print(f"Error in get_orders: {str(e)}")
            return []
    
    def get_orders_by_date_range(self, start_date: str, end_date: str):
        """Get orders between two dates."""
        try:
            print(f"Fetching orders between {start_date} and {end_date}")
            
            # Ensure we're authenticated
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get orders by date range")
                return []
                
            response = self.session.get(
                f"{self.base_url}/orders/date-range/", 
                params={"start_date": start_date, "end_date": end_date},
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                orders = response.json()
                print(f"Retrieved {len(orders)} orders in date range from API")
                
                # Format orders to ensure all expected fields are present
                formatted_orders = []
                for order in orders:
                    try:
                        formatted_order = {
                            "id": order.get("id", ""),
                            "order_time": order.get("order_time", ""),
                            "customer_name": order.get("customer_name", "Unknown"),
                            "phone_number": order.get("phone_number", "N/A"),
                            "total": float(order.get("total", 0)),
                            "status": order.get("status", "pending"),
                            "delivery_method": order.get("delivery_method", "N/A"),
                            "wilaya": order.get("wilaya", "N/A"),
                            "commune": order.get("commune", "N/A"),
                            "notes": order.get("notes", ""),
                            "items": order.get("items", [])
                        }
                        formatted_orders.append(formatted_order)
                    except Exception as item_error:
                        print(f"Error processing order: {str(item_error)}")
                        continue

                return formatted_orders
                
            else:
                print(f"Error getting orders by date range: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in get_orders_by_date_range: {str(e)}")
            return []
    
    def get_order_details(self, order_id: str):
        """Get detailed information for a specific order."""
        try:
            print(f"Getting detailed information for order {order_id}")
            
            # Try to get from the API first
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get order details")
                return None
                
            response = self.session.get(
                f"{self.base_url}/orders/{order_id}", 
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"Retrieved order {order_id} details from API")
                return order
            elif response.status_code == 404:
                print(f"Order {order_id} not found")
                return None
            else:
                print(f"Error retrieving order: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_order_details: {str(e)}")
            return None
    
    def create_sale(self, items: list, total: float):
        """Create a new sale with the provided items."""
        try:
            print(f"Creating sale with {len(items)} items")
            
            if not self._ensure_authenticated():
                print("Authentication failed, cannot create sale")
                return None
                
            # Create sale items in the format expected by the API
            sale_items = []
            
            # Process each item
            for item in items:
                try:
                    # Get variant_id from barcode
                    variant_response = self.session.get(
                        f"{self.base_url}/variantsbarcode/{item['barcode']}", 
                        headers=self.get_headers(),
                        timeout=10
                    )
                    
                    if variant_response.status_code == 200:
                        variant = variant_response.json()
                        sale_items.append({
                            "variant_id": variant["id"],
                            "quantity": item["quantity"],
                            "price": item["price"]
                        })
                    else:
                        print(f"API error for barcode {item['barcode']}: {variant_response.status_code}")
                        return None
                except Exception as item_error:
                    print(f"Error processing item: {str(item_error)}")
                    return None

            # Create the sale
            data = {
                "items": sale_items,
                "total": total
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/sales", 
                    json=data, 
                    headers=self.get_headers(),
                    timeout=15
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    # Clear sales cache after creating a new sale
                    self.clear_cache("sales_")
                    return response.json()
                else:
                    print(f"Error creating sale: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error posting sale: {str(e)}")
                return None
                
        except Exception as e:
            print(f"Error creating sale: {str(e)}")
            return None
    
    def get_stats(self):
        """Get overall statistics summary with sales data, order counts, revenue and top products."""
        try:
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get stats")
                return {}
                
            response = self.session.get(
                f"{self.base_url}/stats/", 
                headers=self.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Retrieved stats data from API")
                if not isinstance(data, dict):
                    print(f"Unexpected response type: {type(data)}")
                    return {}
                
                # Ensure all required fields exist
                data.setdefault('total_sales', 0)
                data.setdefault('total_orders', 0)
                data.setdefault('total_revenue', 0)
                data.setdefault('top_products', [])
                
                return data
            else:
                print(f"Error getting stats: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error in get_stats: {str(e)}")
            return {}
            
    # Dummy data methods have been removed as they are no longer needed
    # since we always use real data from the database
