def get_inventory(self) -> List[Dict[str, Any]]:
    """Get all variants with their product information for inventory management."""
    try:
        print("Getting variants from API...")
        # Get all variants first with timeout
        try:
            response = requests.get(
                f"{self.base_url}/variants", 
                headers=self.get_headers(),
                timeout=10  # 10 second timeout for initial request
            )
            if response.status_code != 200:
                print(f"Error getting variants: {response.status_code}")
                if response.status_code == 401:
                    print("Authentication error - please log in again")
                elif response.status_code == 404:
                    print("Variants endpoint not found - check server URL")
                else:
                    print(f"Server response: {response.text}")
                return []

            variants = response.json()
            if not variants:
                print("No variants found in inventory")
                return []
            print(f"Retrieved {len(variants)} variants")

        except requests.Timeout:
            print("Timeout while getting variants - server taking too long to respond")
            return []
        except requests.ConnectionError:
            print("Connection error - check if the server is running")
            return []
        except Exception as e:
            print(f"Unexpected error getting variants: {str(e)}")
            return []

        # Collect unique product IDs
        product_ids = {variant['product_id'] for variant in variants}
        print(f"Found {len(product_ids)} unique products to fetch")
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
                        "id": variant["id"],  # Include variant ID
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
