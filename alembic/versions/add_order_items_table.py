"""add_order_items_table

Revision ID: add_order_items_table
Revises: fefbebdaaffb
Create Date: 2025-06-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_order_items_table_rev'
down_revision: Union[str, None] = 'fefbebdaaffb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old foreign key from orders to variants
    op.drop_constraint('orders_variant_id_fkey', 'orders', type_='foreignkey')
    
    # Drop variant_id and quantity columns from orders
    op.drop_column('orders', 'variant_id')
    op.drop_column('orders', 'quantity')
    
    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('variant_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Add back variant_id and quantity columns to orders
    op.add_column('orders', sa.Column('variant_id', sa.Integer(), nullable=True))
    op.add_column('orders', sa.Column('quantity', sa.Integer(), nullable=True))
    
    # Add back foreign key from orders to variants
    op.create_foreign_key('orders_variant_id_fkey', 'orders', 'variants', ['variant_id'], ['id'])
    
    # Drop order_items table
    op.drop_table('order_items')
