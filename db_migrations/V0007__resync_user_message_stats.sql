-- Пересинхронизируем user_message_stats с реальными данными из messages
-- Обновляем существующие записи
UPDATE t_p77610913_ai_dating_bot.user_message_stats ums
SET 
    total_messages = subq.msg_count,
    updated_at = subq.last_msg
FROM (
    SELECT 
        user_id, 
        COUNT(*) as msg_count,
        MAX(created_at) as last_msg
    FROM t_p77610913_ai_dating_bot.messages
    WHERE sender = 'user'
    GROUP BY user_id
) subq
WHERE ums.user_id = subq.user_id;

-- Добавляем новых пользователей которых нет в stats
INSERT INTO t_p77610913_ai_dating_bot.user_message_stats (user_id, total_messages, updated_at)
SELECT 
    user_id, 
    COUNT(*) as total_messages,
    MAX(created_at) as updated_at
FROM t_p77610913_ai_dating_bot.messages
WHERE sender = 'user' 
  AND user_id NOT IN (SELECT user_id FROM t_p77610913_ai_dating_bot.user_message_stats)
GROUP BY user_id;