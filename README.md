# Shiakati Store Backend

A robust FastAPI-based backend system for managing an e-commerce store with support for both in-store sales and online orders.

## Features

### 1. Authentication

- Secure JWT-based authentication system
- Admin user management with encrypted passwords
- Protected API endpoints

### 2. Product Management

- Create, read, update, and delete products
- Product categorization
- Support for product variants (size, color, etc.)
- Barcode-based product identification
- Inventory tracking

### 3. Sales Management

- Process in-store sales
- Real-time inventory updates
- Sales history tracking
- Variant-based sales tracking

### 4. Order Management

- Online order processing
- Multiple delivery methods (home/desk delivery)
- Order status tracking (pending/shipped/delivered)
- Customer information management
- Inventory validation on order placement

### 5. Statistics and Reporting

- Sales summary statistics
- Inventory status reporting
- Top-selling products analysis
- Combined sales and orders revenue tracking
- Profit calculations (30% margin)

### 6. Categories Management

- Dynamic category management
- Category-based product organization
- Flexible category structure

## Technical Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Environment Management**: python-dotenv

## API Endpoints

### Authentication

- `POST /auth/login` - User authentication

### Products

- `GET /products` - List all products
- `GET /products/{product_id}` - Get product details
- `POST /products` - Create new product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product

### Variants

- `GET /variants` - List all variants
- `GET /variants/{variant_id}` - Get variant details
- `POST /variants` - Create new variant
- `PUT /variants/{variant_id}` - Update variant
- `DELETE /variants/{variant_id}` - Delete variant

### Sales

- `GET /sales` - List all sales
- `GET /sales/{sale_id}` - Get sale details
- `POST /sales` - Create new sale

### Orders

- `GET /orders` - List all orders
- `GET /orders/{order_id}` - Get order details
- `POST /orders` - Create new order
- `PUT /orders/{order_id}` - Update order status

### Categories

- `GET /categories` - List all categories

### Statistics

- `GET /stats/summary` - Get overall statistics
- `GET /stats/inventory` - Get inventory statistics
- `GET /stats/top-products` - Get top-selling products

## Database Schema

### admin_users

- id (PK)
- username (unique)
- hashed_password

### products

- id (PK)
- name
- description
- category
- created_at

### variants

- id (PK)
- product_id (FK)
- size
- color
- barcode (unique)
- price
- quantity
- created_at

### sales

- id (PK)
- variant_id (FK)
- quantity
- sale_time

### orders

- id (PK)
- customer_name
- phone_number
- age
- wilaya
- commune
- delivery_method (home/desk)
- variant_id (FK)
- quantity
- order_time
- status

## Setup and Installation

1. Create a PostgreSQL database

```bash
createuser -P shiakati
createdb -O shiakati shiakati
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set up environment variables
   Create a `.env` file with:

```
DATABASE_URL=postgresql://shiakati:shiakati@localhost:5432/shiakati
SECRET_KEY=your_secret_key
```

4. Run database migrations

```bash
alembic upgrade head
```

5. Seed initial data

```bash
python -m app.db.seed
```

6. Start the server

```bash
uvicorn app.main:app --reload
```

## Default Admin Credentials

- Username: admin
- Password: admin123

## API Documentation

Once the server is running, access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
