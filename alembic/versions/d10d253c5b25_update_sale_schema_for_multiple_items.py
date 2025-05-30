"""Update sale schema for multiple items

Revision ID: d10d253c5b25
Revises: 72e0960643ba
Create Date: 2025-05-29 10:00:00.000000

"""
from typing import Sequence, Union
from decimal import Decimal
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd10d253c5b25'
down_revision: Union[str, None] = '72e0960643ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new sales table structure
    op.drop_table('sales')
    
    # Update variants table to use decimal quantity
    with op.batch_alter_table('variants') as batch_op:
        batch_op.alter_column('quantity',
                            existing_type=sa.Integer(),
                            type_=sa.Numeric(10, 3),
                            postgresql_using='quantity::numeric(10,3)')
    
    # Create new sales table
    op.create_table(
        'sales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('sale_time', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Create sale_items table
    op.create_table(
        'sale_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id', ondelete='CASCADE')),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('variants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('quantity', sa.Numeric(10, 3), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False)
    )


def downgrade() -> None:
    # Drop the new tables
    op.drop_table('sale_items')
    op.drop_table('sales')
    
    # Restore variants quantity to integer
    with op.batch_alter_table('variants') as batch_op:
        batch_op.alter_column('quantity',
                            existing_type=sa.Numeric(10, 3),
                            type_=sa.Integer(),
                            postgresql_using='quantity::integer')
    
    # Restore original sales table
    op.create_table(
        'sales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('variants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('quantity', sa.Integer(), server_default=sa.text('1')),
        sa.Column('sale_time', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
