-- Create expenses table based on the SQLAlchemy model
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    category VARCHAR NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    description TEXT,
    expense_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on expense_date for faster querying by date
CREATE INDEX idx_expenses_date ON expenses (expense_date);
