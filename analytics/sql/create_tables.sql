CREATE DATABASE IF NOT EXISTS habit_tracker;

DROP TABLE IF EXISTS habit_events;

CREATE TABLE habit_events (
    event_id UUID,
    event_type String,
    timestamp DateTime,
    user_id UInt32,
    habit_id UInt32,
    habit_name String,
    completed_date Date,
    streak_before UInt16,
    streak_after UInt16,
    is_milestone Bool,
    milestone_type Nullable(String)
) ENGINE = MergeTree()
ORDER BY (toYYYYMMDD(timestamp), user_id, habit_id);
