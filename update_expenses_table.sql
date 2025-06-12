-- Add payment_method column to expenses table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'expenses' 
        AND column_name = 'payment_method'
    ) THEN
        ALTER TABLE expenses ADD COLUMN payment_method VARCHAR DEFAULT 'Cash';
    END IF;
END$$;
