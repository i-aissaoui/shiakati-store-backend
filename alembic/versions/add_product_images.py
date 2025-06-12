"""Add image fields to products

Revision ID: add_product_images
Depends on: fefbebdaaffb

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_product_images'
down_revision = 'fefbebdaaffb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('image_url', sa.Text(), nullable=True))
    op.add_column('products', sa.Column('additional_images', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('products', 'additional_images')
    op.drop_column('products', 'image_url')
