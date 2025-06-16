"""add website visibility column

Revision ID: add_website_visibility_column
Revises: 
Create Date: 2023-06-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_website_visibility_column'
down_revision = 'add_image_url_products_rev'  # Using the latest migration as parent
branch_labels = None
depends_on = None


def upgrade():
    # Add show_on_website column to products table if it doesn't exist
    op.execute("""
    ALTER TABLE products ADD COLUMN IF NOT EXISTS show_on_website INTEGER DEFAULT 0 NOT NULL;
    """)
    
    # Add image_url column if it doesn't exist
    op.execute("""
    ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT DEFAULT NULL;
    """)


def downgrade():
    # Remove show_on_website column
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_column('show_on_website')
        batch_op.drop_column('image_url')
