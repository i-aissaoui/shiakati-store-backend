"""Update schema structure

Revision ID: b05a9c8e1a91
Revises: 49d828b5bdf2
Create Date: 2025-05-22 20:45:27.193855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b05a9c8e1a91'
down_revision: Union[str, None] = '49d828b5bdf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop existing tables (keeping admin_users)
    op.drop_table('sale_items')
    op.drop_table('sales')
    op.drop_table('products')
    op.drop_table('categories')
    
    # Create new tables according to the schema
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('size', sa.Text(), nullable=True),
        sa.Column('color', sa.Text(), nullable=True),
        sa.Column('barcode', sa.Text(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('quantity', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('barcode')
    )
    
    op.create_table('sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('variant_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), server_default=sa.text('1'), nullable=True),
        sa.Column('sale_time', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.Text(), nullable=True),
        sa.Column('phone_number', sa.Text(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('wilaya', sa.Text(), nullable=True),
        sa.Column('commune', sa.Text(), nullable=True),
        sa.Column('delivery_method', sa.Text(), nullable=True),
        sa.Column('variant_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), server_default=sa.text('1'), nullable=True),
        sa.Column('order_time', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('status', sa.Text(), server_default=sa.text("'pending'"), nullable=True),
        sa.CheckConstraint("delivery_method IN ('home', 'desk')"),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    # Drop tables
    op.drop_table('orders')
    op.drop_table('sales')
    op.drop_table('variants')
    op.drop_table('products')
    
    # Recreate original tables
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_categories_id', 'categories', ['id'], unique=False)
    
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('barcode', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_id', 'products', ['id'], unique=False)
    
    op.create_table('sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('total', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sales_id', 'sales', ['id'], unique=False)
    
    op.create_table('sale_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sale_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['sale_id'], ['sales.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sale_items_id', 'sale_items', ['id'], unique=False)
