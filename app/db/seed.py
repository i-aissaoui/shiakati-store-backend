from sqlalchemy.orm import Session
from app.db.models import AdminUser, Product, Variant, Category
from app.core.security import get_password_hash
from app.db.session import SessionLocal
import app.db.models as models

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

def seed_categories(db: Session):
    """Seed initial categories"""
    categories = [
        {"name": "Vêtements", "description": "Tout type de vêtements"},
        {"name": "Chaussures", "description": "Chaussures pour hommes, femmes et enfants"},
        {"name": "Accessoires", "description": "Sacs, ceintures, bijoux, etc."},
        {"name": "Sport", "description": "Équipement et vêtements de sport"},
        {"name": "Beauté", "description": "Produits de beauté et cosmétiques"},
        {"name": "Maison", "description": "Décoration et articles pour la maison"},
    ]
    
    for category_data in categories:
        # Check if category exists
        exists = db.query(models.Category).filter(
            models.Category.name == category_data["name"]
        ).first()
        
        if not exists:
            category = models.Category(**category_data)
            db.add(category)
    
    db.commit()
    print(f"Added {len(categories)} categories")
        
def seed_sample_products(db: Session):
    """Seed sample products and variants if none exist"""
    try:
        # First ensure we have categories
        seed_categories(db)
        
        # Get category IDs with error handling
        categories = {}
        for name in ["Vêtements", "Chaussures", "Sport"]:
            category = db.query(models.Category).filter(models.Category.name == name).first()
            if not category:
                print(f"Warning: Category {name} not found")
                continue
            categories[name] = category.id
        
        if not categories:
            print("Error: No categories found. Cannot seed products.")
            return
            
        # Check if we already have products
        product_count = db.query(models.Product).count()
        if product_count > 0:
            print(f"Database already has {product_count} products, skipping seed")
            return
            
        # Sample products with category IDs
        products = [
            {
                "name": "T-Shirt Classic",
                "description": "T-shirt 100% coton de haute qualité",
                "category_id": categories.get("Vêtements")
            },
            {
                "name": "Jean Regular",
                "description": "Jean confortable coupe régulière",
                "category_id": categories.get("Vêtements")
            },
            {
                "name": "Baskets Running",
                "description": "Chaussures de course légères",
                "category_id": categories.get("Sport")
            },
            {
                "name": "Sneakers Urban",
                "description": "Sneakers tendance pour la ville",
                "category_id": categories.get("Chaussures")
            }
        ]
        
        # Filter out products with missing category IDs
        products = [p for p in products if p["category_id"] is not None]
        
        if not products:
            print("Error: No valid products to seed")
            return
            
        # Create products
        db_products = []
        for product_data in products:
            try:
                product = models.Product(**product_data)
                db.add(product)
                db.flush()  # Get the product ID
                db_products.append(product)
            except Exception as e:
                print(f"Error creating product {product_data['name']}: {str(e)}")
                continue
        
        # Create variants for each product
        for product in db_products:
            prefix = str(product.id).zfill(3)
            variants = []
            
            if "T-Shirt" in product.name:
                for size in ["S", "M", "L"]:
                    for color in ["White", "Black"]:
                        variants.append({
                            "product_id": product.id,
                            "size": size,
                            "color": color,
                            "barcode": f"TS-{size}-{color[:3].upper()}-{prefix}",
                            "price": 19.99,
                            "quantity": 25
                        })
            elif "Jean" in product.name:
                for size in ["32", "34", "36"]:
                    variants.append({
                        "product_id": product.id,
                        "size": size,
                        "color": "Blue",
                        "barcode": f"JN-{size}-BLU-{prefix}",
                        "price": 49.99,
                        "quantity": 15
                    })
            else:  # Shoes
                for size in ["40", "41", "42", "43", "44"]:
                    variants.append({
                        "product_id": product.id,
                        "size": size,
                        "color": "Black",
                        "barcode": f"SH-{size}-BLK-{prefix}",
                        "price": 79.99,
                        "quantity": 10
                    })
            
            # Add variants
            for variant_data in variants:
                try:
                    variant = models.Variant(**variant_data)
                    db.add(variant)
                except Exception as e:
                    print(f"Error creating variant for product {product.name}: {str(e)}")
                    continue
        
        # Commit all changes
        try:
            db.commit()
            print(f"Added {len(db_products)} products with their variants")
        except Exception as e:
            db.rollback()
            print(f"Error committing changes: {str(e)}")
            raise
            
    except Exception as e:
        db.rollback()
        print(f"Error in seed_sample_products: {str(e)}")
        raise

def seed_db():
    """Run all seed functions"""
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_categories(db)
        seed_sample_products(db)
        print("Database seeding complete")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
