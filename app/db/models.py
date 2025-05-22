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

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    variants = relationship("Variant", back_populates="product", cascade="all, delete-orphan")

class Variant(Base):
    __tablename__ = "variants"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    size = Column(Text, nullable=True)
    color = Column(Text, nullable=True)
    barcode = Column(Text, unique=True, nullable=False)
    price = Column(Numeric(10, 2))
    quantity = Column(Integer, server_default=text("0"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    sales = relationship("Sale", back_populates="variant")
    orders = relationship("Order", back_populates="variant")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey("variants.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, server_default=text("1"))
    sale_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    variant = relationship("Variant", back_populates="sales")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(Text)
    phone_number = Column(Text)
    age = Column(Integer)
    wilaya = Column(Text)
    commune = Column(Text)
    delivery_method = Column(Text)
    variant_id = Column(Integer, ForeignKey("variants.id"))
    quantity = Column(Integer, server_default=text("1"))
    order_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status = Column(Text, server_default=text("'pending'"))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("delivery_method IN ('home', 'desk')"),
    )
    
    # Relationships
    variant = relationship("Variant", back_populates="orders") 