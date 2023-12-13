-- Add up migration script here
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    board TEXT NOT NULL,
    thread_number BIGINT NOT NULL,
    post_number BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    is_gunpride INT DEFAULT 0,
    is_toxic INT DEFAULT 0,
    checked_toxic INT DEFAULT 0,
    data TEXT,
    html TEXT
)