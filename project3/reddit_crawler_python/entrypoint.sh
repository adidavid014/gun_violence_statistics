#!/usr/bin/sh

sqlx database create
sqlx migrate run

wait-for-it.sh postgres:5432 -- python /reddit_app/reddit_crawler.py &

tail -f /dev/null