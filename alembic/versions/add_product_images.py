"""add product images

Revision ID: add_product_images_rev
Revises: add_website_visibility_column
Create Date: 2025-06-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_product_images_rev'
down_revision = 'add_website_visibility_column'
branch_labels = None
depends_on = None


def upgrade():
    # This is a placeholder migration to maintain the dependency chain
    pass


def downgrade():
    pass