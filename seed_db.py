from app.db.seed import seed_admin_user, seed_categories, seed_sample_products
from app.db.session import SessionLocal, engine
from app.db.models import Base

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = SessionLocal()
    try:
        # Seed admin user
        seed_admin_user(db)
        
        # Seed categories
        seed_categories(db)
        
        # Seed sample products and variants
        seed_sample_products(db)
        
        print("Database initialized and seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
