-- Create a temporary table without the image_url column
CREATE TABLE products_temp (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Copy data from the existing products table to the temp table
INSERT INTO products_temp SELECT id, name, description, category_id, created_at FROM products;

-- Drop the original table
DROP TABLE products;

-- Rename the temp table to products
ALTER TABLE products_temp RENAME TO products;

-- Recreate any indexes or triggers if needed
