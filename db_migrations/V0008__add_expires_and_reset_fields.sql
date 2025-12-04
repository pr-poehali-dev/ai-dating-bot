-- Добавляем поле expires_at для разовых покупок (24 часа)
ALTER TABLE t_p77610913_ai_dating_bot.purchases 
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;

-- Добавляем поле last_reset_date для отслеживания сброса дневного лимита сообщений
ALTER TABLE t_p77610913_ai_dating_bot.user_message_stats 
ADD COLUMN IF NOT EXISTS last_reset_date DATE DEFAULT CURRENT_DATE;