-- 1. Drop existing tables if they exist
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS variants;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS admin_users;

-- 2. Create admin_users table
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

-- 3. Create products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create variants table
CREATE TABLE variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    size TEXT,
    color TEXT,
    barcode TEXT UNIQUE NOT NULL,
    price NUMERIC(10, 2),
    quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create sales table
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    variant_id INTEGER REFERENCES variants(id) ON DELETE SET NULL,
    quantity INTEGER DEFAULT 1,
    sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Create orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name TEXT,
    phone_number TEXT,
    age INTEGER,
    wilaya TEXT,
    commune TEXT,
    delivery_method TEXT CHECK (delivery_method IN ('home', 'desk')),
    variant_id INTEGER REFERENCES variants(id),
    quantity INTEGER DEFAULT 1,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);
