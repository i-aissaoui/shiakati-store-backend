from app.db.session import SessionLocal
from app.db.seed_orders import seed_orders

def main():
    db = SessionLocal()
    try:
        print("Seeding orders...")
        seed_orders(db)
        print("Done seeding orders.")
    except Exception as e:
        print(f"Error seeding orders: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
