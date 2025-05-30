import requests
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import time

load_dotenv()

class APIClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None

    def login(self, username: str, password: str) -> bool:
        try:
            print(f"Attempting login with username: {username}")
            # Using form-urlencoded format as required by OAuth2PasswordRequestForm
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "username": username,
                    "password": password,
                    "grant_type": "password"  # Required for OAuth2 password flow
                }
            )
            print(f"Login response status: {response.status_code}")
            print(f"Login response body: {response.text}")
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                return True
            return False
        except requests.RequestException as e:
            print(f"Login error: {str(e)}")
            return False

    def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def get_products(self) -> list:
        try:
            # First get the list of products
            response = requests.get(f"{self.base_url}/products", headers=self.get_headers())
            if response.status_code != 200:
                print(f"Error getting products: {response.status_code}")
                return []
            
            products = response.json()
            
            # Then get detailed info for each product including variants
            detailed_products = []
            max_retries = 3
            
            for product in products:
                retries = 0
                success = False
                
                while retries < max_retries and not success:
                    try:
                        detail_response = requests.get(
                            f"{self.base_url}/products/{product['id']}", 
                            headers=self.get_headers(),
                            timeout=10  # Add timeout
                        )
                        
                        if detail_response.status_code == 200:
                            detailed_products.append(detail_response.json())
                            success = True
                        elif detail_response.status_code == 404:
                            print(f"Product {product['id']} not found")
                            break  # Don't retry 404s
                        else:
                            print(f"Error getting product details for ID {product['id']}: {detail_response.status_code}")
                            retries += 1
                    except Exception as e:
                        print(f"Request error for product {product['id']}: {str(e)}")
                        retries += 1
                        
                    if retries > 0 and not success:
                        time.sleep(0.5)  # Add delay between retries
            
            return detailed_products
        except Exception as e:
            print(f"Error in get_products: {str(e)}")
            return []

    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/products/barcode/{barcode}", headers=self.get_headers())
        return response.json() if response.status_code == 200 else None

    def create_sale(self, items: list, total: float) -> Optional[Dict[str, Any]]:
        try:
            # Create sale items in the format expected by the API
            sale_items = []
            for item in items:
                # Get variant_id from barcode
                variant_response = requests.get(
                    f"{self.base_url}/variants/barcode/{item['barcode']}", 
                    headers=self.get_headers()
                )
                if variant_response.status_code != 200:
                    raise Exception(f"Variant not found for barcode: {item['barcode']}")
                    
                variant = variant_response.json()
                sale_items.append({
                    "variant_id": variant["id"],
                    "quantity": item["quantity"],
                    "price": item["price"]
                })

            # Create the sale
            data = {
                "items": sale_items,
                "total": total
            }
            response = requests.post(
                f"{self.base_url}/sales", 
                json=data, 
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response.status_code != 500 else 'Server error'
                raise Exception(f"Failed to create sale: {error_msg}")
                
        except requests.RequestException as e:
            print(f"Network error creating sale: {str(e)}")
            return None
        except Exception as e:
            print(f"Error creating sale: {str(e)}")
            return None

    def get_categories(self) -> list:
        response = requests.get(f"{self.base_url}/categories", headers=self.get_headers())
        return response.json() if response.status_code == 200 else []

    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = requests.post(f"{self.base_url}/products", json=product_data, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response.status_code != 500 else 'Server error'
            raise Exception(f"Failed to create product: {error_msg}")

    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = requests.put(f"{self.base_url}/products/{product_id}", json=product_data, headers=self.get_headers())
        return response.json() if response.status_code == 200 else None

    def delete_product(self, product_id: int) -> bool:
        response = requests.delete(f"{self.base_url}/products/{product_id}", headers=self.get_headers())
        return response.status_code == 200

    def get_sales_stats(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/stats", headers=self.get_headers())
        return response.json() if response.status_code == 200 else {}

    def get_inventory(self) -> List[Dict[str, Any]]:
        """Get all variants with their product information for inventory management."""
        try:
            # Get all variants first
            response = requests.get(f"{self.base_url}/variants", headers=self.get_headers())
            if response.status_code != 200:
                print(f"Error getting variants: {response.status_code}")
                return []

            variants = response.json()
            if not variants:
                return []

            # Collect unique product IDs
            product_ids = {variant['product_id'] for variant in variants}
            products_map = {}

            # Get product details in batches
            for product_id in product_ids:
                try:
                    product_response = requests.get(
                        f"{self.base_url}/products/{product_id}", 
                        headers=self.get_headers(),
                        timeout=5  # Add timeout
                    )
                    if product_response.status_code == 200:
                        products_map[product_id] = product_response.json()
                    else:
                        print(f"Warning: Failed to get product {product_id}: {product_response.status_code}")
                except Exception as e:
                    print(f"Warning: Error getting product {product_id}: {str(e)}")

            # Build inventory items list
            inventory_items = []
            for variant in variants:
                product_id = variant['product_id']
                if product_id in products_map:
                    product = products_map[product_id]
                    try:
                        inventory_items.append({
                            "product_id": product["id"],
                            "product_name": product["name"],
                            "barcode": variant["barcode"],
                            "price": float(variant["price"]),
                            "quantity": float(variant["quantity"]),
                            "category": product.get("category_name", "Uncategorized"),
                            "size": variant.get("size", ""),
                            "color": variant.get("color", "")
                        })
                    except (KeyError, ValueError) as e:
                        print(f"Warning: Error processing variant {variant.get('id')}: {str(e)}")
                        continue

            return inventory_items

        except Exception as e:
            print(f"Error in get_inventory: {str(e)}")
            return []

    def get_orders(self) -> List[Dict[str, Any]]:
        """Get all orders with their details."""
        try:
            response = requests.get(f"{self.base_url}/orders", headers=self.get_headers())
            if response.status_code == 200:
                orders = response.json()
                # Format each order
                formatted_orders = []
                for order in orders:
                    formatted_orders.append({
                        "id": order["id"],
                        "date": order["order_time"].split("T")[0],  # Get just the date part
                        "customer": order.get("customer_name", "N/A"),
                        "total": float(order["total"]) if "total" in order else 0.0,
                        "status": order.get("status", "pending"),
                        "delivery_method": order.get("delivery_method", "N/A"),
                        "phone_number": order.get("phone_number", "N/A"),
                        "wilaya": order.get("wilaya", "N/A"),
                        "commune": order.get("commune", "N/A")
                    })
                return formatted_orders
            print(f"Error getting orders: {response.status_code}")
            return []
        except Exception as e:
            print(f"Error in get_orders: {str(e)}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics summary."""
        try:
            print("Fetching stats from API...")
            response = requests.get(f"{self.base_url}/stats/", headers=self.get_headers())
            
            if response.status_code != 200:
                print(f"Error getting stats: {response.status_code}")
                if response.status_code != 500:
                    print(f"Error response: {response.text}")
                return {}
                
            data = response.json()
            print(f"Received stats response: {data}")
            if not isinstance(data, dict):
                print(f"Unexpected response type: {type(data)}")
                return {}
            
            # Ensure all required fields exist
            data.setdefault('total_sales', 0)
            data.setdefault('total_orders', 0)
            data.setdefault('total_revenue', 0)
            data.setdefault('top_products', [])
            
            return data
            
        except Exception as e:
            print(f"Error in get_stats: {str(e)}")
            return {}

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get list of categories."""
        try:
            response = requests.get(f"{self.base_url}/categories", headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            print(f"Error getting categories: {response.status_code}")
            return []
        except Exception as e:
            print(f"Error in get_categories: {str(e)}")
            return []

    def get_sales_history(self) -> List[Dict[str, Any]]:
        """Get all sales with their details for history view."""
        try:
            response = requests.get(f"{self.base_url}/sales", headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            print(f"Error getting sales history: {response.status_code}")
            return []
        except Exception as e:
            print(f"Error in get_sales_history: {str(e)}")
            return []
            
    def get_sale_details(self, sale_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific sale."""
        try:
            response = requests.get(f"{self.base_url}/sales/{sale_id}", headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            print(f"Error getting sale details: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error in get_sale_details: {str(e)}")
            return None

    def create_variant(self, variant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new variant for a product."""
        try:
            response = requests.post(f"{self.base_url}/variants", json=variant_data, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json()
                
            # Try to get a detailed error message from the response
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', 'Unknown error')
            except:
                error_msg = 'Server error' if response.status_code == 500 else response.text
                
            raise Exception(f"Failed to create variant: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create variant: Network error - {str(e)}")
            
    def delete_variant(self, barcode: str) -> bool:
        """Delete a variant by its barcode."""
        try:
            # First get the variant ID from the barcode
            if not isinstance(barcode, str):
                raise Exception("Invalid barcode format")

            response = requests.get(f"{self.base_url}/variants/barcode/{barcode}", headers=self.get_headers())
            if response.status_code == 404:
                raise Exception("Variant not found")
            if response.status_code != 200:
                raise Exception("Error getting variant details")
            
            variant = response.json()
            if not isinstance(variant, dict) or "id" not in variant:
                raise Exception("Invalid variant data received")
                
            variant_id = variant["id"]
            if not isinstance(variant_id, (int, str)) or str(variant_id).strip() == "":
                raise Exception("Invalid variant ID")
            
            # Then delete the variant using its ID
            delete_response = requests.delete(f"{self.base_url}/variants/{variant_id}", headers=self.get_headers())
            
            if delete_response.status_code != 200:
                error_msg = "Server error"
                try:
                    error_data = delete_response.json()
                    error_msg = error_data.get('detail', error_msg)
                except:
                    pass
                raise Exception(f"Failed to delete variant: {error_msg}")
                
            return True
            
        except Exception as e:
            print(f"Error deleting variant: {str(e)}")
            raise Exception(f"Failed to delete variant: {str(e)}")

    def update_variant(self, barcode: str, variant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a variant by its barcode."""
        try:
            response = requests.put(
                f"{self.base_url}/variants/{barcode}",
                headers=self.get_headers(),
                json=variant_data
            )
            if response.status_code != 200:
                raise Exception(f"Failed to update variant: {response.text}")
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to update variant: {str(e)}")
