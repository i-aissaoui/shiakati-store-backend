import requests
import time
import datetime
import random
import os
from typing import Dict, Any, Optional, List

class APIClient:
    def __init__(self):
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

    def transform_product_fields(self, products):
        """Transform product field names from API format to UI format.
        
        API format uses: 'name', 'barcode', 'price', etc.
        UI expects: 'product_name', 'barcode', 'price', 'stock', etc.
        """
        transformed_products = []
        
        for product in products:
            # Create a new dict with the transformed field names
            transformed = {
                # Map 'name' directly to 'product_name' without appending variant info
                "product_name": product.get("name", "Unknown Product"),
                
                # Keep 'barcode' field as is or generate one from product ID
                "barcode": product.get("barcode", f"SKU{product.get('id', '')}"),
                
                # Keep 'price' field as is
                "price": product.get("price", 0),
                
                # Map 'quantity' or 'inventory' to 'stock' expected by the UI
                "stock": product.get("quantity", product.get("inventory", product.get("total_stock", 0))),
                
                # Add empty size and color fields for consistent display in the UI
                "size": "",
                "color": "",
                
                # Include category name
                "category": product.get("category_name", "Uncategorized"),
                
                # Include product ID for reference
                "product_id": product.get("id"),
                
                # Make sure we include description for product details
                "description": product.get("description", ""),
                
                # Keep all original fields too
                **product
            }
            transformed_products.append(transformed)
            
        return transformed_products
        
    def get_combined_inventory(self):
        """Get inventory combining variants and products data for a complete view.
        
        This method fetches both products and variants, then combines them to create
        proper inventory items with all necessary fields for the UI.
        """
        try:
            # Check if we need to auto-login
            if not self.token:
                print("No token found, attempting auto-login...")
                self.login("admin", "123")
                
            # First get all products (setting high limit to get all products)
            products_response = self.session.get(
                f"{self.base_url}/products?limit=1000", 
                headers=self.get_headers(),
                timeout=10
            )
            
            if products_response.status_code != 200:
                print(f"Failed to get products: {products_response.status_code}")
                return self._generate_dummy_inventory(15)
                
            products = products_response.json()
            print(f"Retrieved {len(products)} products")
            
            # Create a product lookup map
            products_map = {product["id"]: product for product in products}
            
            # Get all variants (setting high limit to get all variants)
            variants_response = self.session.get(
                f"{self.base_url}/variants?limit=1000", 
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
                            # IMPORTANT: Use ONLY the product name without any variant info
                            "product_name": product.get('name', 'Unknown'),
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
                
                # If we found variants, return them
                if inventory_items:
                    print(f"Created {len(inventory_items)} inventory items from variants")
                    return inventory_items
            
            # If no variants or error getting variants, transform products directly
            print("Using only product data for inventory (no variants)")
            return self.transform_product_fields(products)
            
        except Exception as e:
            print(f"Error in get_combined_inventory: {e}")
            return self._generate_dummy_inventory(15)

    def login(self, username: str, password: str) -> bool:
        try:
            print(f"Attempting login with username: {username}")
            # Using form-urlencoded format as required by OAuth2PasswordRequestForm
            response = self.session.post(
                f"{self.base_url}/auth/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "username": username,
                    "password": password,
                    "grant_type": "password"  # Required for OAuth2 password flow
                },
                timeout=10  # 10 second timeout for login
            )
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                # Extract and store the actual token from the response
                token_data = response.json()
                if "access_token" in token_data:
                    self.token = token_data["access_token"]
                    print("Successfully logged in and stored token")
                    return True
                else:
                    print("Missing token in response")
                    return False
            else:
                print(f"Login failed with status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"Login error: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error during login: {str(e)}")
            return False

    def get_headers(self, skip_content_type: bool = False) -> Dict[str, str]:
        """Get headers for API requests.
        
        Args:
            skip_content_type: If True, don't include Content-Type header.
                               Useful for multipart/form-data uploads.
        
        Returns:
            Dict containing headers
        """
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Add Content-Type header unless told to skip it (for file uploads)
        if not skip_content_type:
            headers["Content-Type"] = "application/json"
            
        return headers

    def get_sales_history(self) -> List[Dict[str, Any]]:
        """Get list of all sales with their details for history view."""
        try:
            print("Attempting to get sales history...")
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get sales history")
                return []
                
            # Try to get from the API
            try:
                response = self.session.get(
                    f"{self.base_url}/sales", 
                    headers=self.get_headers(),
                    timeout=30
                )
                if response.status_code == 200:
                    sales = response.json()
                    print(f"Retrieved {len(sales)} sales from API")
                    return sales
                elif response.status_code == 401:
                    print("Authentication required for sales history")
                    return []
                else:
                    print(f"Error getting sales history: {response.status_code}")
                    return []
                
            except requests.RequestException as e:
                print(f"Network error in get_sales_history: {str(e)}")
                return []
                
        except Exception as e:
            print(f"Error in get_sales_history: {str(e)}")
            return []
            
    def clear_sales_history(self) -> bool:
        """Clear all sales history from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("Attempting to clear sales history...")
            if not self._ensure_authenticated():
                print("Authentication failed, cannot clear sales history")
                return False
                
            try:
                response = self.session.delete(
                    f"{self.base_url}/sales/clear-all", 
                    headers=self.get_headers(),
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Successfully cleared sales history: {result.get('message', 'Success')}")
                    # Clear any cached sales data
                    self.clear_cache("sales_")
                    return True
                elif response.status_code == 401:
                    print("Authentication required to clear sales history")
                    return False
                else:
                    print(f"Error clearing sales history: {response.status_code}")
                    return False
                    
            except requests.RequestException as e:
                print(f"Network error in clear_sales_history: {str(e)}")
                return False
                
        except Exception as e:
            print(f"Error in clear_sales_history: {str(e)}")
            return False

    def get_orders(self) -> List[Dict[str, Any]]:
        """Get all orders with their details."""
        try:
            print("=== API CLIENT: Fetching orders ===")
            
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get orders")
                # Return empty list instead of dummy data
                return []
                
            response = self.session.get(f"{self.base_url}/orders", headers=self.get_headers(), timeout=30)
            if response.status_code == 401:
                print("Authentication required for orders")
                # Login must be handled by the UI
                return []
            
            if response.status_code != 200:
                print(f"Error getting orders: {response.status_code}")
                return []

            orders = response.json()
            if not orders:
                print("No orders found")
                return []

            print(f"API CLIENT: Processing {len(orders)} orders...")
            
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

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get list of categories."""
        try:
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get categories")
                return self._generate_dummy_categories()
                
            response = self.session.get(f"{self.base_url}/categories", 
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                categories = response.json()
                print(f"Retrieved {len(categories)} categories from API")
                return categories
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    print("Re-authenticated successfully, retrying request...")
                    return self.get_categories()
                else:
                    print("Re-authentication failed")
                    return self._generate_dummy_categories()
            else:
                print(f"Error getting categories: {response.status_code}")
                # For demo purposes, return dummy data
                return self._generate_dummy_categories()
        except Exception as e:
            print(f"Error in get_categories: {str(e)}")
            return self._generate_dummy_categories()
    
    def _generate_dummy_categories(self):
        """Generate dummy category data for testing and offline mode."""
        print("Generating dummy categories for offline mode")
        
        # Standard retail categories
        categories = [
            {"id": 1, "name": "Vêtements", "description": "Tous types de vêtements"},
            {"id": 2, "name": "Chaussures", "description": "Chaussures pour hommes, femmes et enfants"},
            {"id": 3, "name": "Accessoires", "description": "Sacs, ceintures, bijoux et accessoires"},
            {"id": 4, "name": "Sports", "description": "Équipement et vêtements de sport"},
            {"id": 5, "name": "Beauté", "description": "Produits de beauté et de soins personnels"},
            {"id": 6, "name": "Électronique", "description": "Gadgets et accessoires électroniques"},
            {"id": 7, "name": "Maison", "description": "Articles pour la maison et décoration"}
        ]
        
        return categories

    def get_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses with improved error handling and authentication."""
        try:
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get expenses")
                return []
                
            response = self.session.get(
                f"{self.base_url}/expenses", # Removed trailing slash to avoid routing issues
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                expenses = response.json()
                print(f"Retrieved {len(expenses)} expenses from API")
                return expenses
            elif response.status_code == 401:
                # Only try to re-authenticate once to avoid infinite loop
                print("Authentication error (401), trying to login once...")
                self.login("admin", "123")
                
                # Make a second attempt after login
                response = self.session.get(
                    f"{self.base_url}/expenses", 
                    headers=self.get_headers(),
                    timeout=30
                )
                
                if response.status_code == 200:
                    expenses = response.json()
                    print(f"Retrieved {len(expenses)} expenses from API after re-auth")
                    return expenses
                else:
                    print(f"Failed to get expenses after re-auth: {response.status_code}")
                    return []
            else:
                print(f"Error getting expenses: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error in get_expenses: {str(e)}")
            return []
        
    def _generate_dummy_expenses(self, count=10):
        """Generate dummy expense data for testing and offline mode."""
        print(f"Generating {count} dummy expenses for offline mode")
        
        # Common expense categories
        categories = ["Loyer", "Salaires", "Marketing", "Fournitures", "Équipement", "Maintenance", "Électricité", "Eau", "Internet", "Transport"]
        
        # Create dummy expenses
        current_date = datetime.datetime.now()
        dummy_expenses = []
        
        for i in range(1, count + 1):
            # Random date within the last 60 days
            days_ago = random.randint(1, 60)
            expense_date = current_date - datetime.timedelta(days=days_ago)
            
            category = random.choice(categories)
            amount = round(random.uniform(1000, 50000), 2)  # Amount in DZD
            
            expense = {
                "id": i,
                "expense_date": expense_date.strftime("%Y-%m-%d"),
                "amount": amount,
                "category": category,
                "description": f"{category} - {expense_date.strftime('%b %Y')}",
                "notes": f"Note de test pour dépense #{i}" if random.random() > 0.7 else ""
            }
            
            dummy_expenses.append(expense)
        
        return dummy_expenses

    def create_sale(self, items: list, total: float) -> Optional[Dict[str, Any]]:
        """Create a new sale with the provided items.
        
        Args:
            items: List of items in the sale with at least barcode, quantity and price
            total: Total amount of the sale
            
        Returns:
            The created sale data or None if there was an error
        """
        try:
            print(f"=== API CLIENT: Creating sale with {len(items)} items ===")
            if not self._ensure_authenticated():
                print("Authentication failed, generating offline sale")
                return self._generate_dummy_sale_response(items, total)
                
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
                        # Use a fallback ID for offline mode
                        sale_items.append({
                            "variant_id": f"offline-{item['barcode']}",
                            "quantity": item["quantity"],
                            "price": item["price"]
                        })
                except Exception as item_error:
                    print(f"Error processing item: {str(item_error)}")
                    # Continue with next item
                    continue

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
                    return self._generate_dummy_sale_response(items, total)
            except Exception as e:
                print(f"Error posting sale: {str(e)}")
                return self._generate_dummy_sale_response(items, total)
                
        except Exception as e:
            print(f"Error creating sale: {str(e)}")
            return self._generate_dummy_sale_response(items, total)

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics summary with sales data, order counts, revenue and top products."""
        try:
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get stats")
                return self._generate_dummy_stats()
                
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
                    return self._generate_dummy_stats()
                
                # Ensure all required fields exist
                data.setdefault('total_sales', 0)
                data.setdefault('total_orders', 0)
                data.setdefault('total_revenue', 0)
                data.setdefault('top_products', [])
                
                return data
            else:
                print(f"Error getting stats: {response.status_code}")
                return self._generate_dummy_stats()
        except Exception as e:
            print(f"Error in get_stats: {str(e)}")
            return self._generate_dummy_stats()
    
    def _generate_dummy_stats(self) -> Dict[str, Any]:
        """Generate dummy stats data for offline mode."""
        print("Generating dummy stats for offline mode")
        
        # Create random top products
        product_names = [
            "T-shirt en coton", "Jeans slim fit", "Veste en cuir", 
            "Robe d'été", "Chemise formelle", "Chaussures de sport",
            "Sac à main", "Ceinture en cuir", "Chapeau de soleil"
        ]
        category_names = ["Vêtements", "Chaussures", "Accessoires"]
        
        top_products = []
        for i in range(5):
            name = product_names[i % len(product_names)]
            category = category_names[i % len(category_names)]
            total_sales = random.randint(10, 100)
            price = random.randint(1000, 5000)
            
            top_products.append({
                'id': i + 1,
                'name': name,
                'category_name': category,
                'total_sales': total_sales,
                'total_revenue': total_sales * price,
                'current_stock': random.randint(5, 50)
            })
            
        # Generate overall stats
        total_sales_count = sum(p['total_sales'] for p in top_products)
        total_revenue = sum(p['total_revenue'] for p in top_products)
        
        return {
            'total_sales': total_sales_count,
            'total_orders': random.randint(int(total_sales_count * 0.7), total_sales_count),
            'total_revenue': total_revenue,
            'top_products': top_products
        }

    def _generate_dummy_orders(self, count=5):
        """Generate dummy orders data for testing and offline mode."""
        print(f"Generating {count} dummy orders for offline mode")
        
        # Common Algerian wilayas and communes for realistic test data
        wilayas = ["Alger", "Oran", "Constantine", "Annaba", "Batna", "Blida"]
        communes = {
            "Alger": ["Bab Ezzouar", "Hydra", "El Biar", "Kouba"],
            "Oran": ["Bir El Djir", "Es Senia", "Arzew"],
            "Constantine": ["El Khroub", "Ain Smara"],
            "Annaba": ["El Bouni", "Sidi Amar"],
            "Batna": ["Tazoult", "Timgad"],
            "Blida": ["Boufarik", "Beni Mered"]
        }
        product_names = [
            "T-shirt en coton", "Jeans slim fit", "Veste en cuir", 
            "Robe d'été", "Chemise formelle", "Chaussures de sport",
            "Sac à main", "Ceinture en cuir", "Chapeau de soleil"
        ]
        
        colors = ["Rouge", "Bleu", "Noir", "Blanc", "Vert", "Jaune", "Marron"]
        sizes = ["S", "M", "L", "XL", "XXL"]
        delivery_methods = ["Standard", "Express", "Point de collecte", "Livraison à domicile"]
        statuses = ["pending", "processing", "shipped", "delivered", "canceled"]
        
        # Create dummy orders
        dummy_orders = []
        for i in range(1, count + 1):
            # Random date within the last 30 days
            days_ago = random.randint(1, 30)
            order_date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            # Random customer info
            wilaya = random.choice(wilayas)
            commune = random.choice(communes.get(wilaya, ["Centre"]))
            
            # Generate between 1 and 4 items for this order
            item_count = random.randint(1, 4)
            items = []
            total = 0
            
            for j in range(1, item_count + 1):
                product_name = random.choice(product_names)
                price = round(random.uniform(1000, 5000), 2)  # Price in DZD
                quantity = random.randint(1, 3)
                size = random.choice(sizes)
                color = random.choice(colors)
                
                item_total = price * quantity
                total += item_total
                
                items.append({
                    "id": i * 100 + j,
                    "product_name": product_name,
                    "price": price,
                    "quantity": quantity,
                    "size": size,
                    "color": color,
                    "total": item_total
                })
            
            # Create order object
            order = {
                "id": i,
                "order_time": order_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "customer_name": f"Client Test {i}",
                "phone_number": f"05{random.randint(10000000, 99999999)}",
                "total": round(total, 2),
                "status": random.choice(statuses),
                "delivery_method": random.choice(delivery_methods),
                "wilaya": wilaya,
                "commune": commune,
                "notes": f"Commande de test #{i}" if random.random() > 0.7 else "",
                "items": items
            }
            
            dummy_orders.append(order)
        
        return dummy_orders

    def _generate_dummy_sale_response(self, items: list, total: float) -> Dict[str, Any]:
        """Generate a dummy sale response for offline mode.
        
        Args:
            items: List of items in the sale
            total: Total amount of the sale
            
        Returns:
            A dictionary simulating a successful sale response
        """
        print("Generating dummy sale response for offline mode")
        
        # Create a unique sale ID using timestamp
        sale_id = f"offline-{int(datetime.datetime.now().timestamp())}"
        sale_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Create formatted items
        formatted_items = []
        for idx, item in enumerate(items):
            formatted_items.append({
                "id": f"{sale_id}-item-{idx + 1}",
                "sale_id": sale_id,
                "product_name": item.get("name", f"Product {item.get('barcode', 'Unknown')}"),
                "variant_id": f"offline-{item.get('barcode', f'item-{idx}')}",
                "quantity": item["quantity"],
                "price": item["price"],
                "barcode": item.get("barcode", ""),
                "size": item.get("size", ""),
                "color": item.get("color", "")
            })
        
        # Create the sale response
        sale_response = {
            "id": sale_id,
            "sale_time": sale_time,
            "total": total,
            "items": formatted_items,
            "offline_mode": True,  # Flag to indicate this was created offline
            "status": "completed"
        }
        
        # Store in memory for later retrieval
        cache_key = f"sale_{sale_id}"
        self._cache[cache_key] = sale_response
        self._cache_timeout[cache_key] = time.time()
        
        return sale_response
    
    def get_order_details(self, order_id: str):
        """Get detailed information for a specific order."""
        try:
            print(f"Getting detailed information for order {order_id}")
            
            # Try to get from the API first
            try:
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
                elif response.status_code == 401:
                    if self._handle_auth_error(response):
                        print("Re-authenticated successfully, retrying request...")
                        # Recursive call after re-authentication
                        return self.get_order_details(order_id)
                    else:
                        print("Re-authentication failed")
            except Exception as e:
                print(f"API request error: {str(e)}")
            
            # If API request failed, try to get it from all orders
            print("Attempting to find order in cached orders data")
            orders = self.get_orders()
            for order in orders:
                if str(order.get("id", "")) == str(order_id):
                    print(f"Found order {order_id} in cached orders data")
                    return order
                    
            print(f"Order {order_id} not found")
            return None
        except Exception as e:
            print(f"Error in get_order_details: {str(e)}")
            return None

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
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    print("Re-authenticated successfully, retrying request...")
                    # Recursive call after re-authentication
                    return self.get_sale_details(sale_id)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Error retrieving sale: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_sale_details: {str(e)}")
            return None

    def get_order(self, order_id: str):
        """Get order by ID (alias for get_order_details for backward compatibility)."""
        return self.get_order_details(order_id)
        
    def _ensure_authenticated(self):
        """Ensure we have a valid authentication token."""
        if not self.token:
            print("No authentication token found, requiring login...")
            return False
        return True
        
    def _handle_auth_error(self, response):
        """Handle 401 authentication errors by attempting to re-authenticate.
        Returns True if authentication was attempted, False otherwise.
        """
        if response.status_code == 401:
            print("Authentication error (401), will need to login...")
            self.token = None  # Clear the token to force re-login
            return False
        return False
        
    def clear_cache(self, cache_key: str = None):
        """Clear the cache for a specific key or all cache if key is None."""
        if cache_key is None:
            self._cache = {}
            self._cache_timeout = {}
            print("Cleared all cache")
        elif cache_key in self._cache:
            del self._cache[cache_key]
            if cache_key in self._cache_timeout:
                del self._cache_timeout[cache_key]
            print(f"Cleared cache for {cache_key}")
        elif cache_key.endswith("_"):
            # Clear all keys with matching prefix
            prefix = cache_key
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._cache[k]
                if k in self._cache_timeout:
                    del self._cache_timeout[k]
            print(f"Cleared {len(keys_to_delete)} cache entries with prefix '{prefix}'")
    
    def get_inventory(self) -> List[Dict[str, Any]]:
        """Get all variants with their product information for inventory management.
        
        This method fetches data from the API with proper field transformations to ensure
        all UI expected fields are present.
        """
        try:
            # Use cache if available
            cache_key = "inventory_data"
            if cache_key in self._cache and (time.time() - self._cache_timeout.get(cache_key, 0)) < 300:
                print("Using cached inventory data")
                return self._cache[cache_key]
            
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get inventory")
                return self._generate_dummy_inventory()
                
            try:
                # First attempt to use get_combined_inventory which has better handling for variants
                print("Getting inventory using combined approach...")
                inventory_items = self.get_combined_inventory()
                
                # Store in cache
                self._cache[cache_key] = inventory_items
                self._cache_timeout[cache_key] = time.time()
                
                return inventory_items
                
            except Exception as e:
                print(f"Error using combined inventory approach: {str(e)}")
                # Fall back to direct variant fetching
                return self._fetch_variants_with_products()
                
        except Exception as e:
            print(f"Error in get_inventory: {str(e)}")
            return self._generate_dummy_inventory()
            
    def _fetch_variants_with_products(self) -> List[Dict[str, Any]]:
        """Fetch variants and their associated products directly from API."""
        try:
            response = self.session.get(
                f"{self.base_url}/variants", 
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                variants = response.json()
                if not variants:
                    print("No variants found in inventory")
                    return []
                print(f"Retrieved {len(variants)} variants")
                
                # Collect unique product IDs
                product_ids = {variant['product_id'] for variant in variants}
                products_map = {}
                
                # Get product details for each variant
                for product_id in product_ids:
                    product_response = self.session.get(
                        f"{self.base_url}/products/{product_id}", 
                        headers=self.get_headers(),
                        timeout=10
                    )
                    if product_response.status_code == 200:
                        products_map[product_id] = product_response.json()
                    elif product_response.status_code == 401:
                        if self._handle_auth_error(product_response):
                            # Try again after re-authentication
                            product_response = self.session.get(
                                f"{self.base_url}/products/{product_id}", 
                                headers=self.get_headers(),
                                timeout=10
                            )
                            if product_response.status_code == 200:
                                products_map[product_id] = product_response.json()
                
                # Build inventory items list
                inventory_items = []
                for variant in variants:
                    product_id = variant.get('product_id')
                    if product_id in products_map:
                        product = products_map[product_id]
                        try:
                            inventory_item = {
                                "variant_id": variant.get("id"),
                                "product_id": product.get("id"),
                                "product_name": f"{product.get('name', 'Unknown')} - {variant.get('color', '')} ({variant.get('size', '')})",
                                "category": product.get("category_name", "Uncategorized"),
                                "barcode": variant.get("barcode", ""),
                                "size": variant.get("size", ""),
                                "color": variant.get("color", ""),
                                "stock": variant.get("quantity", 0),
                                "quantity": variant.get("quantity", 0),  # Add quantity field for UI compatibility
                                "price": float(variant.get("price", 0)),
                                "cost_price": float(variant.get("cost_price", 0)),
                                "description": product.get("description", "")
                            }
                            inventory_items.append(inventory_item)
                        except Exception as e:
                            print(f"Error processing variant: {str(e)}")
                
                # Cache the results
                cache_key = "inventory_data"
                self._cache[cache_key] = inventory_items
                self._cache_timeout[cache_key] = time.time()
                
                return inventory_items
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    return self._fetch_variants_with_products()
                else:
                    return self._generate_dummy_inventory()
            else:
                print(f"Error retrieving inventory: {response.status_code}")
                return self._generate_dummy_inventory()
        except Exception as e:
            print(f"Error in _fetch_variants_with_products: {str(e)}")
            return self._generate_dummy_inventory()
    
    def _generate_dummy_inventory(self, count=20):
        """Generate dummy inventory data for testing and offline mode.
        
        This creates realistic product data with variants that can be used
        when the API is not available or for testing.
        
        Args:
            count: Number of inventory items to generate
            
        Returns:
            List of inventory items with all required fields for UI
        """
        print(f"Generating {count} dummy inventory items for offline mode")
        
        categories = ["Vêtements", "Chaussures", "Accessoires", "Électronique", "Maison"]
        sizes = ["S", "M", "L", "XL", "XXL", "N/A"]
        colors = ["Rouge", "Bleu", "Noir", "Blanc", "Vert", "Jaune", "Marron", "N/A"]
        product_names = [
            "T-shirt en coton", "Jeans slim fit", "Veste en cuir", 
            "Robe d'été", "Chemise formelle", "Chaussures de sport",
            "Sac à main", "Ceinture en cuir", "Chapeau de soleil", 
            "Montre classique", "Collier en argent", "Lunettes de soleil",
            "Sandales de plage", "Bottes d'hiver", "Écharpe en laine",
            "Pantalon chino", "Short de sport", "Maillot de bain",
            "Casquette", "Gants en cuir"
        ]
        
        inventory_items = []
        for i in range(1, count + 1):
            product_name = product_names[i % len(product_names)]
            category = categories[i % len(categories)]
            size = sizes[i % len(sizes)]
            color = colors[i % len(colors)]
            stock = i * 10
            price = round(i * 1.5, 2)
            cost = round(i * 1.2, 2)
            barcode = f"123456789012{i}"
            
            # Create full name with variant details
            full_name = product_name
            if color != "N/A":
                full_name += f" - {color}"
            if size != "N/A":
                full_name += f" ({size})"
            
            inventory_items.append({
                "variant_id": f"variant_{i}",
                "product_id": f"product_{i}",
                "product_name": full_name,
                "category": category,
                "barcode": barcode,
                "size": size,
                "color": color,
                "stock": stock,
                "quantity": stock,  # Add quantity field for UI compatibility
                "price": price,
                "cost_price": cost
            })
        
        return inventory_items

    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get a product by its ID.
        
        Args:
            product_id: The ID of the product to retrieve
            
        Returns:
            A dictionary with the product data or None if not found
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot get product")
            return None
            
        try:
            print(f"Fetching product with ID: {product_id}")
            response = self.session.get(
                f"{self.base_url}/products/{product_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                product = response.json()
                print(f"Successfully retrieved product ID: {product.get('id')}")
                return product
            elif response.status_code == 404:
                print(f"Product with ID {product_id} not found")
                return None
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.get_product_by_id(product_id)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Failed to get product. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in get_product_by_id: {str(e)}")
            return None

    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing product.
        
        Args:
            product_id: The ID of the product to update
            product_data: A dictionary with the product data to update
            
        Returns:
            The updated product data or None if there was an error
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot update product")
            return None
            
        try:
            print(f"Updating product with ID: {product_id}")
            print(f"Update data: {product_data}")
            response = self.session.put(
                f"{self.base_url}/products/{product_id}",
                json=product_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                product = response.json()
                print(f"Successfully updated product ID: {product.get('id')}")
                # Clear any cached inventory data
                self.clear_cache("inventory_")
                return product
            elif response.status_code == 404:
                print(f"Product with ID {product_id} not found")
                return None
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.update_product(product_id, product_data)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Failed to update product. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    pass
                return None
                
        except Exception as e:
            print(f"Error in update_product: {str(e)}")
            return None

    def delete_variant(self, variant_id: int) -> bool:
        """Delete a variant by its ID.
        
        Args:
            variant_id: The ID of the variant to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot delete variant")
            return False
            
        try:
            print(f"Deleting variant with ID: {variant_id}")
            response = self.session.delete(
                f"{self.base_url}/variants/{variant_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Successfully deleted variant ID: {variant_id}")
                # Clear any cached inventory data
                self.clear_cache("inventory_")
                return True
            elif response.status_code == 404:
                print(f"Variant with ID {variant_id} not found")
                return False
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.delete_variant(variant_id)
                else:
                    print("Re-authentication failed")
                    return False
            else:
                print(f"Failed to delete variant. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in delete_variant: {str(e)}")
            return False

    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new product.
        
        Args:
            product_data: A dictionary with the product data
            
        Returns:
            The created product data or None if there was an error
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot create product")
            return None
            
        try:
            print(f"Creating new product: {product_data.get('name', 'Unknown')}")
            response = self.session.post(
                f"{self.base_url}/products",
                json=product_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                product = response.json()
                print(f"Successfully created product ID: {product.get('id')}")
                # Clear any cached inventory data
                self.clear_cache("inventory_")
                return product
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.create_product(product_data)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Failed to create product. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in create_product: {str(e)}")
            return None

    def create_variant(self, variant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new variant for a product.
        
        Args:
            variant_data: A dictionary with the variant data including product_id
            
        Returns:
            The created variant data or None if there was an error
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot create variant")
            return None
            
        try:
            print(f"Creating new variant for product ID: {variant_data.get('product_id')}")
            response = self.session.post(
                f"{self.base_url}/variants",
                json=variant_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                variant = response.json()
                print(f"Successfully created variant ID: {variant.get('id')}")
                # Clear any cached inventory data
                self.clear_cache("inventory_")
                return variant
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.create_variant(variant_data)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Failed to create variant. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in create_variant: {str(e)}")
            return None

    def update_variant(self, variant_id: int, variant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing variant.
        
        Args:
            variant_id: The ID of the variant to update
            variant_data: A dictionary with the variant data to update
            
        Returns:
            The updated variant data or None if there was an error
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot update variant")
            return None
            
        try:
            print(f"Updating variant with ID: {variant_id}")
            response = self.session.put(
                f"{self.base_url}/variants/{variant_id}",
                json=variant_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                variant = response.json()
                print(f"Successfully updated variant ID: {variant.get('id')}")
                # Clear any cached inventory data
                self.clear_cache("inventory_")
                return variant
            elif response.status_code == 404:
                print(f"Variant with ID {variant_id} not found")
                return None
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.update_variant(variant_id, variant_data)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Failed to update variant. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in update_variant: {str(e)}")
            return None

    def upload_product_image(self, barcode: str, image_path: str) -> bool:
        """Upload a product image for a specific variant barcode.
        
        Args:
            barcode: The barcode of the variant to associate the image with
            image_path: The local path to the image file
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot upload image")
            return False
            
        try:
            print(f"Uploading image for barcode: {barcode}")
            
            # Check if the image file exists
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return False
                
            # Open file in binary mode
            with open(image_path, 'rb') as image_file:
                # Create multipart form data
                files = {'file': (os.path.basename(image_path), image_file, 'image/jpeg')}
                
                # Use headers without Content-Type as it will be set by the request
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                
                response = self.session.post(
                    f"{self.base_url}/products/upload-image/{barcode}",
                    files=files,
                    headers=headers,
                    timeout=30  # Longer timeout for image uploads
                )
                
                if response.status_code == 200:
                    print(f"Successfully uploaded image for barcode: {barcode}")
                    return True
                elif response.status_code == 401:
                    if self._handle_auth_error(response):
                        # Try again after re-authentication
                        return self.upload_product_image(barcode, image_path)
                    else:
                        print("Re-authentication failed")
                        return False
                else:
                    print(f"Failed to upload image. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error in upload_product_image: {str(e)}")
            return False

    def delete_product(self, product_id: int) -> bool:
        """Delete a product by its ID.
        
        Args:
            product_id: The ID of the product to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot delete product")
            return False
            
        try:
            print(f"Deleting product with ID: {product_id}")
            response = self.session.delete(
                f"{self.base_url}/products/{product_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Successfully deleted product ID: {product_id}")
                # Clear any cached inventory data
                self.clear_cache("inventory_")
                return True
            elif response.status_code == 404:
                print(f"Product with ID {product_id} not found")
                return False
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.delete_product(product_id)
                else:
                    print("Re-authentication failed")
                    return False
            else:
                print(f"Failed to delete product. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in delete_product: {str(e)}")
            return False

    def generate_unique_barcode(self) -> str:
        """Generate a unique barcode for a new product or variant.
        
        Returns:
            A unique barcode string
        """
        try:
            # Try to get from API first
            if self._ensure_authenticated():
                try:
                    response = self.session.get(
                        f"{self.base_url}/utils/generate-barcode",
                        headers=self.get_headers(),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "barcode" in data:
                            return data["barcode"]
                except Exception as e:
                    print(f"Error generating barcode from API: {str(e)}")
            
            # Fallback to generating locally if API call fails
            import time
            import random
            
            # Use timestamp plus random numbers to ensure uniqueness
            timestamp = int(time.time())
            random_part = random.randint(1000, 9999)
            
            # Format: SKU + timestamp + random
            barcode = f"SKU{timestamp % 10000}{random_part}"
            
            print(f"Generated local barcode: {barcode}")
            return barcode
                
        except Exception as e:
            print(f"Error in generate_unique_barcode: {str(e)}")
            # Last resort fallback
            import time
            return f"SKU{int(time.time())}"
        
    def get_variants_by_product_id(self, product_id: int) -> List[Dict[str, Any]]:
        """Get all variants for a specific product ID.
        
        Args:
            product_id: The product ID to find variants for
            
        Returns:
            A list of variant dictionaries, or empty list if none found
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot get variants")
            return []
            
        try:
            print(f"Fetching variants for product ID: {product_id}")
            response = self.session.get(
                f"{self.base_url}/variants/product/{product_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                variants = response.json()
                print(f"Found {len(variants)} variants for product ID {product_id}")
                return variants
            elif response.status_code == 404:
                print(f"No variants found for product ID {product_id}")
                return []
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.get_variants_by_product_id(product_id)
                else:
                    print("Re-authentication failed")
                    return []
            else:
                print(f"Error getting variants for product ID {product_id}: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"Error in get_variants_by_product_id: {str(e)}")
            return []
    
    def get_product_images(self, barcode: str) -> List[Dict[str, Any]]:
        """Get all images for a product variant with the specified barcode.
        
        Args:
            barcode: The barcode of the variant to get images for
            
        Returns:
            A list of image URLs or an empty list if no images or error
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot get product images")
            return []
            
        try:
            print(f"\n===== REQUESTING IMAGES =====")
            print(f"Getting product images for barcode: {barcode}")
            
            # Set timeout to prevent hanging
            response = self.session.get(
                f"{self.base_url}/products/product-images/{barcode}",
                headers=self.get_headers(),
                timeout=10
            )
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Debug the structure of the response
                print("\n===== RESPONSE STRUCTURE =====")
                try:
                    if 'images' in result:
                        images = result.get('images', [])
                        print(f"Images found: {len(images)}")
                        print(f"Images type: {type(images)}")
                        
                        # Check the first image format
                        if images and len(images) > 0:
                            first_img = images[0]
                            print(f"First image type: {type(first_img)}")
                            if isinstance(first_img, dict):
                                print(f"First image keys: {list(first_img.keys())}")
                                for key, val in first_img.items():
                                    print(f"  {key}: {val} ({type(val)})")
                            else:
                                print(f"First image value: {first_img}")
                    else:
                        print(f"Response has no 'images' key. Keys found: {list(result.keys())}")
                        print(f"Raw response: {result}")
                except Exception as debug_err:
                    print(f"Error in response debugging: {str(debug_err)}")
                
                # Return the entire result object, not just the images array
                # This allows the caller to access the main_image information as well
                print(f"Successfully got {len(result.get('images', []))} images for barcode: {barcode}")
                print(f"Main image: {result.get('main_image')}")
                return result
                
            elif response.status_code == 404:
                print(f"No images found for barcode: {barcode}")
                return []
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.get_product_images(barcode)
                else:
                    print("Re-authentication failed")
                    return []
            else:
                print(f"Failed to get product images. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"Error in get_product_images: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_product_image(self, barcode: str, filename: str) -> bool:
        """Delete a specific image for a product variant.
        
        Args:
            barcode: The barcode of the variant
            filename: The filename of the image to delete (without path)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot delete product image")
            return False
            
        try:
            print(f"Deleting image {filename} for barcode: {barcode}")
            response = self.session.delete(
                f"{self.base_url}/products/product-image/{barcode}/{filename}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Successfully deleted image {filename} for barcode: {barcode}")
                return True
            elif response.status_code == 404:
                print(f"Image not found for barcode: {barcode}")
                return False
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.delete_product_image(barcode, filename)
                else:
                    print("Re-authentication failed")
                    return False
            else:
                print(f"Failed to delete product image. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in delete_product_image: {str(e)}")
            return False

    def get_product_images_by_id(self, product_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get images for a product by product ID.
        
        Args:
            product_id: The ID of the product
            
        Returns:
            A list of image URLs or None if there was an error
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot get product images")
            return None
            
        try:
            print(f"Getting images for product ID: {product_id}")
            response = self.session.get(
                f"{self.base_url}/product-images/list/{product_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                images = response.json()
                return images
            elif response.status_code == 404:
                print(f"Product images not found for product ID: {product_id}")
                return []
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.get_product_images_by_id(product_id)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Failed to get product images. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in get_product_images_by_id: {str(e)}")
            return None
            
    def upload_product_image(self, product_id: int, image_path: str, set_as_main: bool = False) -> Optional[Dict[str, Any]]:
        """Upload an image for a product.
        
        Args:
            product_id: The ID of the product
            image_path: Path to the image file
            set_as_main: Whether to set this image as the main product image
            
        Returns:
            The image data or None if there was an error
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot upload product image")
            return None
            
        try:
            print(f"Uploading image for product ID: {product_id}")
            
            # Create multipart form data
            files = {'file': open(image_path, 'rb')}
            data = {'set_as_main': 'true' if set_as_main else 'false'}
            
            response = self.session.post(
                f"{self.base_url}/product-images/upload/{product_id}",
                files=files,
                data=data,
                headers=self.get_headers(skip_content_type=True),  # Don't include content-type for multipart/form-data
                timeout=30  # Longer timeout for image upload
            )
            
            if response.status_code in [200, 201]:
                image_data = response.json()
                print(f"Successfully uploaded image for product ID: {product_id}")
                return image_data
            elif response.status_code == 404:
                print(f"Product not found with ID: {product_id}")
                return None
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.upload_product_image(product_id, image_path, set_as_main)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Failed to upload product image. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in upload_product_image: {str(e)}")
            return None
            
    def set_main_product_image(self, product_id: int, image_url: str) -> bool:
        """Set a specific image as the main image for a product.
        
        Args:
            product_id: The ID of the product
            image_url: The URL of the image to set as main
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot set main product image")
            return False
            
        try:
            print(f"Setting main image for product ID: {product_id}")
            
            response = self.session.post(
                f"{self.base_url}/product-images/set-main/{product_id}",
                params={'image_url': image_url},  # Use params instead of json
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Successfully set main image for product ID: {product_id}")
                return True
            elif response.status_code == 404:
                print(f"Product or image not found")
                return False
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.set_main_product_image(product_id, image_url)
                else:
                    print("Re-authentication failed")
                    return False
            else:
                print(f"Failed to set main product image. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in set_main_product_image: {str(e)}")
            return False
            
    def delete_product_image(self, product_id: int, image_url: str) -> bool:
        """Delete a specific image for a product.
        
        Args:
            product_id: The ID of the product
            image_url: The URL of the image to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot delete product image")
            return False
            
        try:
            print(f"Deleting image for product ID: {product_id}, URL: {image_url}")
            
            # Fix: Use query parameter for image_url as expected by the API
            response = self.session.delete(
                f"{self.base_url}/product-images/delete/{product_id}",
                params={'image_url': image_url},  # Use params instead of json
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Successfully deleted image for product ID: {product_id}")
                return True
            elif response.status_code == 404:
                print(f"Product or image not found")
                return False
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.delete_product_image(product_id, image_url)
                else:
                    print("Re-authentication failed")
                    return False
            else:
                print(f"Failed to delete product image. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in delete_product_image: {str(e)}")
            return False
            
    def update_product_visibility(self, product_id: int, show_on_website: int) -> bool:
        """Update whether a product is visible on the website.
        
        Args:
            product_id: The ID of the product
            show_on_website: 0 for hidden, 1 for visible
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Authentication failed, cannot update product visibility")
            return False
            
        try:
            print(f"Updating visibility for product ID: {product_id} to {show_on_website}")
            
            # Fix: Use proper request body format as expected by the updated API
            response = self.session.put(
                f"{self.base_url}/product-images/website-visibility/{product_id}",
                json={'show_on_website': show_on_website},  # This matches the VisibilityUpdate model
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Successfully updated visibility for product ID: {product_id}")
                return True
            elif response.status_code == 404:
                print(f"Product not found with ID: {product_id}")
                return False
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    # Try again after re-authentication
                    return self.update_product_visibility(product_id, show_on_website)
                else:
                    print("Re-authentication failed")
                    return False
            else:
                print(f"Failed to update product visibility. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in update_product_visibility: {str(e)}")
            return False

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order."""
        try:
            print(f"Creating order: {order_data}")
            
            if not self._ensure_authenticated():
                print("Authentication failed, cannot create order")
                return None
                
            response = self.session.post(
                f"{self.base_url}/orders", 
                json=order_data,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                order = response.json()
                print(f"Successfully created order {order.get('id')}")
                return order
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    print("Re-authenticated successfully, retrying request...")
                    return self.create_order(order_data)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Error creating order: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in create_order: {str(e)}")
            return None

    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing order."""
        try:
            print(f"Updating order {order_id}: {order_data}")
            
            if not self._ensure_authenticated():
                print("Authentication failed, cannot update order")
                return None
                
            response = self.session.put(
                f"{self.base_url}/orders/{order_id}", 
                json=order_data,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"Successfully updated order {order_id}")
                return order
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    print("Re-authenticated successfully, retrying request...")
                    return self.update_order(order_id, order_data)
                else:
                    print("Re-authentication failed")
                    return None
            else:
                print(f"Error updating order: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in update_order: {str(e)}")
            return None

    def delete_order(self, order_id: str) -> bool:
        """Delete an order."""
        try:
            print(f"Deleting order {order_id}")
            
            if not self._ensure_authenticated():
                print("Authentication failed, cannot delete order")
                return False
                
            response = self.session.delete(
                f"{self.base_url}/orders/{order_id}",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 204:
                print(f"Successfully deleted order {order_id}")
                return True
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    print("Re-authenticated successfully, retrying request...")
                    return self.delete_order(order_id)
                else:
                    print("Re-authentication failed")
                    return False
            else:
                print(f"Error deleting order: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in delete_order: {str(e)}")
            return False

    def get_customers(self) -> List[Dict[str, Any]]:
        """Get list of customers."""
        try:
            if not self._ensure_authenticated():
                print("Authentication failed, cannot get customers")
                return []
                
            response = self.session.get(
                f"{self.base_url}/customers",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Retrieved {len(customers)} customers from API")
                return customers
            elif response.status_code == 401:
                if self._handle_auth_error(response):
                    print("Re-authenticated successfully, retrying request...")
                    return self.get_customers()
                else:
                    print("Re-authentication failed")
                    return []
            else:
                print(f"Error getting customers: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in get_customers: {str(e)}")
            return []