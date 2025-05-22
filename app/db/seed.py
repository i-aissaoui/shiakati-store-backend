from sqlalchemy.orm import Session
from app.db.models import AdminUser, Product, Variant
from app.core.security import get_password_hash
from app.db.session import SessionLocal

def seed_admin_user(db: Session):
    """Seed admin user if it doesn't exist"""
    existing_admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
    if not existing_admin:
        admin = AdminUser(
            username="admin",
            hashed_password=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("Admin user created: username=admin, password=admin123")
    else:
        print("Admin user already exists")

def seed_sample_products(db: Session):
    """Seed sample products and variants if none exist"""
    product_count = db.query(Product).count()
    if product_count == 0:
        # Sample products
        products = [
            {
                "name": "T-Shirt Classic",
                "description": "100% cotton classic t-shirt",
                "category": "clothing"
            },
            {
                "name": "Jeans Straight Fit",
                "description": "Comfortable straight fit jeans",
                "category": "clothing"
            },
            {
                "name": "Running Shoes",
                "description": "Lightweight running shoes for daily use",
                "category": "footwear"
            }
        ]
        
        db_products = []
        for product_data in products:
            product = Product(**product_data)
            db.add(product)
            db.flush()  # Flush to get the ID
            db_products.append(product)
        
        # Sample variants
        variants = [
            # T-Shirt variants
            {
                "product_id": db_products[0].id,
                "size": "S",
                "color": "White",
                "barcode": "TS-S-WHT-001",
                "price": 19.99,
                "quantity": 25
            },
            {
                "product_id": db_products[0].id,
                "size": "M",
                "color": "White",
                "barcode": "TS-M-WHT-002",
                "price": 19.99,
                "quantity": 30
            },
            {
                "product_id": db_products[0].id,
                "size": "L",
                "color": "Black",
                "barcode": "TS-L-BLK-003",
                "price": 19.99,
                "quantity": 20
            },
            
            # Jeans variants
            {
                "product_id": db_products[1].id,
                "size": "32",
                "color": "Blue",
                "barcode": "JN-32-BLU-001",
                "price": 49.99,
                "quantity": 15
            },
            {
                "product_id": db_products[1].id,
                "size": "34",
                "color": "Blue",
                "barcode": "JN-34-BLU-002",
                "price": 49.99,
                "quantity": 12
            },
            
            # Shoes variants
            {
                "product_id": db_products[2].id,
                "size": "42",
                "color": "Black",
                "barcode": "RS-42-BLK-001",
                "price": 79.99,
                "quantity": 10
            },
            {
                "product_id": db_products[2].id,
                "size": "44",
                "color": "Black",
                "barcode": "RS-44-BLK-002",
                "price": 79.99,
                "quantity": 8
            }
        ]
        
        for variant_data in variants:
            variant = Variant(**variant_data)
            db.add(variant)
        
        db.commit()
        print(f"Added {len(products)} sample products with {len(variants)} variants")
    else:
        print(f"Database already has {product_count} products, skipping seed")

def seed_db():
    """Run all seed functions"""
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_sample_products(db)
        print("Database seeding complete")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
