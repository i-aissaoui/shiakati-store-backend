"""add_image_url_to_products

Revision ID: add_image_url_products_rev
Revises: d10d253c5b25
Create Date: 2025-06-13 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_image_url_products_rev'
down_revision = 'd10d253c5b25' # Set to the latest known valid revision
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('image_url', sa.String(), nullable=True))


def downgrade():
    op.drop_column('products', 'image_url')
