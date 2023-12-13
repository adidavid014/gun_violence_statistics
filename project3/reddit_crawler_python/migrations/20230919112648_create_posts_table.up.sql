-- Add up migration script here
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    subreddit TEXT NOT NULL,
    post_id VARCHAR(16) NOT NULL,
    title varchar(300) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    is_gunpride INT DEFAULT 0,
    is_toxic INT DEFAULT 0,
    checked_toxic INT DEFAULT 0,
    data JSONB DEFAULT '{}'::jsonb NOT NULL,
    html TEXT
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    subreddit TEXT NOT NULL,
    post_id VARCHAR(16) NOT NULL,
    comment_id VARCHAR(16) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    is_gunpride INT DEFAULT 0,
    is_toxic INT DEFAULT 0,
    checked_toxic INT DEFAULT 0,
    data JSONB DEFAULT '{}'::jsonb NOT NULL,
    html TEXT
)