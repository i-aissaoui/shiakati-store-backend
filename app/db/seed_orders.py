from sqlalchemy.orm import Session
from app.db.models import Customer, Order, Variant
from datetime import datetime, timedelta
import random

def seed_orders(db: Session):
    """Seed the database with sample orders."""
    
    # First ensure we have customers
    customers = db.query(Customer).all()
    if not customers:
        # Create some sample customers
        sample_customers = [
            Customer(name="Mohamed Ali", phone_number="0551234567"),
            Customer(name="Fatima Ahmed", phone_number="0661234567"),
            Customer(name="Karim Said", phone_number="0771234567"),
            Customer(name="Amina Belkacem", phone_number="0791234567")
        ]
        db.add_all(sample_customers)
        db.commit()
        customers = sample_customers
    
    # Get available variants
    variants = db.query(Variant).all()
    if not variants:
        raise Exception("No variants found in database. Please seed products and variants first.")
    
    # Sample wilayas and communes
    wilayas = ["Alger", "Oran", "Constantine", "Annaba", "Sétif"]
    communes = {
        "Alger": ["Bab El Oued", "Hussein Dey", "El Harrach", "Bab Ezzouar"],
        "Oran": ["Bir El Djir", "Es Senia", "Arzew", "Ain Turk"],
        "Constantine": ["El Khroub", "Hamma Bouziane", "Ain Smara", "Zighoud Youcef"],
        "Annaba": ["El Bouni", "Sidi Amar", "El Hadjar", "Seraidi"],
        "Sétif": ["El Eulma", "Ain Arnat", "Ain Oulmene", "Bougaa"]
    }
    delivery_methods = ["home", "desk"]
    statuses = ["pending", "confirmed", "processing", "shipped", "delivered"]
    
    # Create sample orders
    sample_orders = []
    base_date = datetime.now() - timedelta(days=30)  # Start from 30 days ago
    
    for i in range(20):  # Create 20 sample orders
        customer = random.choice(customers)
        variant = random.choice(variants)
        wilaya = random.choice(wilayas)
        
        # Calculate total and create items
        num_items = random.randint(1, 3)  # Each order will have 1-3 items
        order_items = []
        total = 0
        
        # Select random variants for this order
        order_variants = random.sample(variants, num_items)
        for variant in order_variants:
            quantity = random.randint(1, 3)
            price = float(variant.price)
            total += price * quantity
            order_items.append({
                'variant_id': variant.id,
                'quantity': quantity,
                'price': price
            })
        
        # Create the order
        order = Order(
            customer_id=customer.id,
            wilaya=wilaya,
            commune=random.choice(communes[wilaya]),
            delivery_method=random.choice(delivery_methods),
            status=random.choice(statuses),
            total=total,
            order_time=base_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            ),
            notes=f"Sample order {i+1}"
        )
        sample_orders.append(order)
    
    # Add orders and create order items
    for order in sample_orders:
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items
        for item_data in order_items:
            item = OrderItem(
                order_id=order.id,
                variant_id=item_data['variant_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.add(item)
            
            # Update variant quantity
            variant = db.query(Variant).filter(Variant.id == item_data['variant_id']).first()
            if variant:
                variant.quantity = max(0, variant.quantity - item_data['quantity'])
    
    db.commit()
    return sample_orders
