CREATE TABLE raw_user_events (
    id SERIAL PRIMARY KEY,
    user_id INT,
    event_type VARCHAR(50),
    event_timestamp TIMESTAMP
);

INSERT INTO raw_user_events (user_id, event_type, event_timestamp) VALUES 
(101, 'login_success', '2026-09-15 10:00:00'),
(102, 'page_view', '2026-09-16 11:30:00'),
(101, 'purchase', '2026-09-18 14:20:00'),
(103, 'login_success', '2026-10-02 09:00:00');