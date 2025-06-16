-- Add cost_price column to variants table
ALTER TABLE variants ADD COLUMN IF NOT EXISTS cost_price NUMERIC(10, 2) DEFAULT 0;
