from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import text
import datetime

Base = declarative_base()

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    category = relationship("Category", back_populates="products")
    variants = relationship("Variant", back_populates="product", cascade="all, delete-orphan")

class Variant(Base):
    __tablename__ = "variants"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    size = Column(Text, nullable=True)
    color = Column(Text, nullable=True)
    barcode = Column(Text, unique=True, nullable=False)
    price = Column(Numeric(10, 2))
    quantity = Column(Numeric(10, 3), server_default=text("0"))  # Allow decimal quantities
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    sale_items = relationship("SaleItem", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total = Column(Numeric(10, 2), nullable=False)
    sale_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    payment_method = Column(Text, server_default=text("'cash'"))
    
    # Relationships
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"))
    variant_id = Column(Integer, ForeignKey("variants.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=False)  # 3 decimal places for precise quantities
    price = Column(Numeric(10, 2), nullable=False)  # 2 decimal places for money
    
    # Relationships
    sale = relationship("Sale", back_populates="items")
    variant = relationship("Variant", back_populates="sale_items")

    @property
    def product_name(self) -> str:
        """Get the product name from the variant relationship."""
        if self.variant and self.variant.product:
            return self.variant.product.name
        return "Unknown Product"

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    phone_number = Column(Text, nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    sales = relationship("Sale", back_populates="customer")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Store price at time of order
    
    # Relationships
    order = relationship("Order", back_populates="items")
    variant = relationship("Variant", back_populates="order_items")
    
    @property
    def product_name(self) -> str:
        """Get the product name from the variant relationship."""
        if self.variant and self.variant.product:
            return self.variant.product.name
        return "Unknown Product"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    wilaya = Column(Text, nullable=False)
    commune = Column(Text, nullable=False)
    delivery_method = Column(Text, nullable=False)
    order_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status = Column(Text, server_default=text("'pending'"))
    notes = Column(Text)
    total = Column(Numeric(10, 2), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("delivery_method IN ('home', 'desk')"),
        CheckConstraint("status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')")
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")