"""Additional methods for the API client class"""

def get_order_details(self, order_id: str):
    """Get detailed information for a specific order.
    
    Args:
        order_id: The ID of the order to retrieve details for
        
    Returns:
        A dictionary with the order details or None if not found
    """
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

def get_order(self, order_id: str):
    """Get order by ID (alias for get_order_details for backward compatibility).
    
    Args:
        order_id: The ID of the order to retrieve
        
    Returns:
        A dictionary with the order data or None if not found
    """
    return self.get_order_details(order_id)
