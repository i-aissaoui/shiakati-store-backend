from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Sale, SaleItem, Product
from session import get_db

def add_test_sales():
    db = next(get_db())
    
    # Get some existing products
    products = db.query(Product).limit(5).all()
    if not products:
        print("No products found in database")
        return
        
    # Create sample sales over the past few days
    base_date = datetime.now()
    sales_data = [
        {
            "items": [
                {"product_id": products[0].id, "quantity": 2, "price": 49.99},
                {"product_id": products[1].id, "quantity": 1, "price": 79.99}
            ]
        },
        {
            "items": [
                {"product_id": products[2].id, "quantity": 1, "price": 29.99},
                {"product_id": products[3].id, "quantity": 3, "price": 19.99}
            ]
        },
        {
            "items": [
                {"product_id": products[0].id, "quantity": 1, "price": 49.99},
                {"product_id": products[4].id, "quantity": 2, "price": 39.99}
            ]
        }
    ]
    
    for i, sale_info in enumerate(sales_data):
        # Create sale with timestamps spaced 1 hour apart
        sale = Sale(
            sale_time=base_date - timedelta(hours=i),
            total=sum(item["price"] * item["quantity"] for item in sale_info["items"])
        )
        db.add(sale)
        db.flush()  # Get the sale ID
        
        # Add sale items
        for item in sale_info["items"]:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=item["price"]
            )
            db.add(sale_item)
    
    db.commit()
    print("Test sales data added successfully")

if __name__ == "__main__":
    add_test_sales()
