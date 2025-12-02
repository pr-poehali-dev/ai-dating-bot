-- Add authentication fields to users table
ALTER TABLE t_p77610913_ai_dating_bot.users 
ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS name VARCHAR(100),
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON t_p77610913_ai_dating_bot.users(email);

-- Update subscriptions table to link with users properly
ALTER TABLE t_p77610913_ai_dating_bot.subscriptions
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;